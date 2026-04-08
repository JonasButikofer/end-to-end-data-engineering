"""
Web Analytics Prefect Flow

Pulls clickstream events from the Adventure Works Web Analytics API and loads
them into Snowflake RAW_EXT.web_analytics_raw using the stage-then-COPY pattern.

Flow steps:
    1. Get watermark from MAX(event_timestamp) in web_analytics_raw
    2. Fetch events from API using since=watermark
    3. Clean, validate, and deduplicate
    4. Upload CSV to @RAW_EXT.WEB_ANALYTICS_STAGE
    5. COPY INTO web_analytics_raw
    6. REMOVE staged files (only on success)
    7. Log summary statistics
"""

import os
import time
import tempfile
import logging
from datetime import datetime, timezone

import requests
import pandas as pd
from dotenv import load_dotenv
from prefect import flow, task, get_run_logger
from snowflake.connector import connect

# Load from project root .env.dev when running locally
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(_root, ".env.dev"))
load_dotenv()  # fallback for Docker (env vars already injected)

# ---------------------------------------------------------------------------
# Snowflake connection
# ---------------------------------------------------------------------------

def get_snowflake_connection():
    return connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "RAW_EXT"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@task(name="get_watermark", retries=2, retry_delay_seconds=5)
def get_watermark() -> str | None:
    """
    Query MAX(event_timestamp) from web_analytics_raw to determine
    the since parameter for the API call. Returns None on first run
    (empty table), which tells the API to default to the last 60 minutes.
    """
    logger = get_run_logger()
    conn = get_snowflake_connection()
    try:
        cs = conn.cursor()
        cs.execute("SELECT MAX(event_timestamp) FROM RAW_EXT.web_analytics_raw")
        row = cs.fetchone()
        watermark = row[0] if row and row[0] else None
        if watermark:
            # Convert to ISO 8601 UTC string for the API since parameter
            if hasattr(watermark, 'isoformat'):
                watermark_str = watermark.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
            else:
                watermark_str = str(watermark)
            logger.info(f"Watermark found: {watermark_str}")
            return watermark_str
        else:
            logger.info("No watermark found (first run). Fetching last 60 minutes.")
            return None
    finally:
        cs.close()
        conn.close()


@task(name="fetch_events", retries=3, retry_delay_seconds=10)
def fetch_events(since: str | None) -> list[dict]:
    """
    Fetch clickstream events from the API. Uses exponential backoff
    for 429 rate limiting and retries on other HTTP errors.
    """
    logger = get_run_logger()
    base_url = os.getenv("API_BASE_URL", "https://is566-web-analytics-api.fly.dev")
    url = f"{base_url}/analytics/clickstream"
    params = {}
    if since:
        params["since"] = since

    max_retries = 5
    backoff = 2

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                events = response.json()
                logger.info(f"Fetched {len(events)} events from API")
                return events
            elif response.status_code == 429:
                wait = backoff ** attempt
                logger.warning(f"Rate limited (429). Waiting {wait}s before retry.")
                time.sleep(wait)
            elif response.status_code == 422:
                logger.error(f"Invalid parameters (422): {response.text}")
                return []
            else:
                logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}. Retrying.")
                time.sleep(backoff ** attempt)
        except requests.exceptions.Timeout:
            logger.warning(f"Request timed out on attempt {attempt + 1}. Retrying.")
            time.sleep(backoff ** attempt)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            time.sleep(backoff ** attempt)

    logger.error("Max retries exceeded. Returning empty event list.")
    return []


@task(name="clean_and_validate")
def clean_and_validate(events: list[dict]) -> pd.DataFrame:
    """
    Cast types, drop nulls on required fields, and deduplicate
    on (session_id, event_type, event_timestamp).
    """
    logger = get_run_logger()

    if not events:
        logger.info("No events to clean.")
        return pd.DataFrame()

    df = pd.DataFrame(events)
    raw_count = len(df)

    # Rename API 'timestamp' -> 'event_timestamp' to match table schema
    df = df.rename(columns={"timestamp": "event_timestamp"})

    # Cast types
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce").astype("Int64")
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], utc=True, errors="coerce")
    df["session_id"] = df["session_id"].astype(str)
    df["page_url"] = df.get("page_url", pd.Series(dtype=str)).astype(str)
    df["event_type"] = df.get("event_type", pd.Series(dtype=str)).astype(str)

    # Drop rows with nulls on required fields
    required = ["customer_id", "product_id", "session_id", "event_timestamp"]
    df = df.dropna(subset=required)

    # Deduplicate on (session_id, event_type, event_timestamp)
    df = df.drop_duplicates(subset=["session_id", "event_type", "event_timestamp"])

    # Keep only table columns (exclude _loaded_at and _file_name — Snowflake handles those)
    df = df[["customer_id", "product_id", "session_id", "page_url", "event_type", "event_timestamp"]]

    # Format timestamp as string for CSV (Snowflake TIMESTAMP_NTZ compatible)
    df["event_timestamp"] = df["event_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")

    clean_count = len(df)
    logger.info(f"Cleaned: {raw_count} raw → {clean_count} after cleaning/dedup "
                f"({raw_count - clean_count} dropped)")
    return df


@task(name="upload_to_stage", retries=2, retry_delay_seconds=5)
def upload_to_stage(df: pd.DataFrame, run_time: datetime) -> str | None:
    """
    Write DataFrame to a temp CSV and PUT it into @RAW_EXT.WEB_ANALYTICS_STAGE.
    Returns the filename on success, None if df is empty.
    """
    logger = get_run_logger()

    if df.empty:
        logger.info("Empty DataFrame — nothing to stage.")
        return None

    stage_name = "RAW_EXT.WEB_ANALYTICS_STAGE"
    filename = f"web_analytics_{run_time.strftime('%Y%m%d_%H%M%S')}.csv"

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, filename)
        df.to_csv(file_path, index=False, na_rep='')

        conn = get_snowflake_connection()
        cs = conn.cursor()
        try:
            cs.execute(f"PUT file://{file_path} @{stage_name}/ OVERWRITE = TRUE")
            logger.info(f"Staged {filename} to @{stage_name}")
        finally:
            cs.close()
            conn.close()

    return filename


@task(name="copy_into_raw", retries=2, retry_delay_seconds=10)
def copy_into_raw() -> dict:
    """
    COPY INTO RAW_EXT.web_analytics_raw from the stage.
    Returns a metrics dict.
    """
    logger = get_run_logger()
    start = time.time()
    stage_name = "RAW_EXT.WEB_ANALYTICS_STAGE"
    table_name = "RAW_EXT.web_analytics_raw"

    conn = get_snowflake_connection()
    try:
        cs = conn.cursor()
        sql = f"""
            COPY INTO {table_name} (customer_id, product_id, session_id, page_url, event_type, event_timestamp)
            FROM @{stage_name}/
            FILE_FORMAT = (
                TYPE = 'CSV'
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                SKIP_HEADER = 1
                NULL_IF = ('')
            )
            ON_ERROR = 'CONTINUE'
        """
        cs.execute(sql)
        rows = cs.fetchall()
        rows_copied = sum(r[3] for r in rows if r[3] is not None)
        rows_skipped = sum(r[4] for r in rows if r[4] is not None)
        cs.close()
        logger.info(f"COPY INTO: {rows_copied} rows copied, {rows_skipped} skipped")
        return {
            "rows_copied": rows_copied,
            "rows_skipped": rows_skipped,
            "execution_time_sec": round(time.time() - start, 2),
            "status": "success",
            "error_message": None,
        }
    except Exception as e:
        logger.error(f"COPY INTO failed: {e}")
        return {
            "rows_copied": 0,
            "rows_skipped": 0,
            "execution_time_sec": round(time.time() - start, 2),
            "status": "error",
            "error_message": str(e),
        }
    finally:
        conn.close()


@task(name="clean_stage")
def clean_stage() -> dict:
    """
    REMOVE all files from @RAW_EXT.WEB_ANALYTICS_STAGE after successful load.
    """
    logger = get_run_logger()
    start = time.time()
    stage_name = "RAW_EXT.WEB_ANALYTICS_STAGE"

    conn = get_snowflake_connection()
    try:
        cs = conn.cursor()
        cs.execute(f"REMOVE @{stage_name}/")
        rows = cs.fetchall()
        cs.close()
        logger.info(f"Stage cleaned: {len(rows)} files removed")
        return {
            "files_removed": len(rows),
            "execution_time_sec": round(time.time() - start, 2),
            "status": "success",
            "error_message": None,
        }
    except Exception as e:
        logger.error(f"Stage cleanup failed: {e}")
        return {
            "files_removed": 0,
            "execution_time_sec": round(time.time() - start, 2),
            "status": "error",
            "error_message": str(e),
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Flow
# ---------------------------------------------------------------------------

@flow(name="web_analytics_flow")
def web_analytics_flow():
    logger = get_run_logger()
    run_time = datetime.now(timezone.utc)

    logger.info("=" * 60)
    logger.info(f"[{run_time.isoformat()}] WEB ANALYTICS FLOW START")
    logger.info("=" * 60)

    # Step 1: Watermark
    since = get_watermark()

    # Step 2: Fetch
    events = fetch_events(since)

    # Step 3: Clean
    df = clean_and_validate(events)

    # Step 4: Stage
    staged_file = upload_to_stage(df, run_time)

    # Step 5 & 6: Copy + cleanup (only if something was staged)
    copy_result = {"rows_copied": 0, "rows_skipped": 0, "status": "skipped", "error_message": None}
    clean_result = {"files_removed": 0, "status": "skipped"}

    if staged_file:
        copy_result = copy_into_raw()
        if copy_result["status"] == "success":
            clean_result = clean_stage()
        else:
            logger.warning("COPY INTO failed — skipping stage cleanup to allow retry.")

    # Step 7: Summary
    logger.info("=" * 60)
    logger.info("CYCLE COMPLETE")
    logger.info(f"  Events fetched:    {len(events)}")
    logger.info(f"  Rows after clean:  {len(df)}")
    logger.info(f"  Rows copied:       {copy_result['rows_copied']}")
    logger.info(f"  Rows skipped:      {copy_result['rows_skipped']}")
    logger.info(f"  Files removed:     {clean_result.get('files_removed', 0)}")
    if copy_result.get("error_message"):
        logger.error(f"  Copy error:        {copy_result['error_message']}")
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Entry point — supports both direct run and scheduled loop
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    interval_minutes = int(os.getenv("FLOW_SCHEDULE_MINUTES", "15"))

    if interval_minutes == 0:
        # Run once and exit
        web_analytics_flow()
    else:
        # Run on a loop
        while True:
            web_analytics_flow()
            print(f"Sleeping {interval_minutes} minutes until next run...")
            time.sleep(interval_minutes * 60)
