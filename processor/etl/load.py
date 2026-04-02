# etl/load.py
import os
import time
import tempfile

def upload_dataframe_to_stage(df, label, stage_name, run_time, file_format="csv"):
    from utils.connections import get_snowflake_connection

    filename = f"{label}_{run_time.strftime('%Y%m%d_%H%M%S')}.{file_format}"
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, filename)

        if file_format == "csv":
            df.to_csv(file_path, index=False, na_rep='')
        elif file_format == "json":
            df.to_json(file_path, orient="records", lines=True)
        else:
            raise ValueError("Unsupported file format for Snowflake upload.")

        print(f"Uploading {filename} to Snowflake stage {stage_name}")

        SNOWFLAKE_SCHEMA=os.getenv("SNOWFLAKE_SCHEMA")

        conn = get_snowflake_connection()
        cs = conn.cursor()
        try:
            cs.execute(f"CREATE SCHEMA IF NOT EXISTS {SNOWFLAKE_SCHEMA};")
            cs.execute(f"CREATE STAGE IF NOT EXISTS {stage_name};")
            cs.execute(f"PUT file://{file_path} @{stage_name}/ OVERWRITE = TRUE")
        finally:
            cs.close()
            conn.close()


def copy_stage_to_table(stage_name, table_name, file_format="CSV", connection=None):
    """
    Execute COPY INTO command to load staged files into a raw table.

    Args:
        stage_name: Name of Snowflake stage (e.g., "orders_stage")
        table_name: Target raw table name (e.g., "orders_raw")
        file_format: File format (CSV or JSON)
        connection: Snowflake connector connection object

    Returns:
        dict with keys: rows_copied, rows_skipped, execution_time_sec, status, error_message
    """
    start = time.time()
    try:
        cs = connection.cursor()
        if file_format.upper() == "CSV":
            sql = f"""
                COPY INTO {table_name}
                FROM @{stage_name}/
                FILE_FORMAT = (
                    TYPE = 'CSV'
                    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                    SKIP_HEADER = 1
                    NULL_IF = ('')
                )
                ON_ERROR = 'CONTINUE'
            """
        else:
            sql = f"""
                COPY INTO {table_name}
                FROM @{stage_name}/
                FILE_FORMAT = (TYPE = 'JSON' STRIP_OUTER_ARRAY = FALSE)
                MATCH_BY_COLUMN_NAME = NONE
                ON_ERROR = 'CONTINUE'
            """
        cs.execute(sql)
        rows = cs.fetchall()
        rows_copied = sum(r[3] for r in rows if r[3] is not None)
        rows_skipped = sum(r[4] for r in rows if r[4] is not None)
        cs.close()
        return {
            "rows_copied": rows_copied,
            "rows_skipped": rows_skipped,
            "execution_time_sec": round(time.time() - start, 2),
            "status": "success",
            "error_message": None,
        }
    except Exception as e:
        return {
            "rows_copied": 0,
            "rows_skipped": 0,
            "execution_time_sec": round(time.time() - start, 2),
            "status": "error",
            "error_message": str(e),
        }


def clean_stage(stage_name, connection=None):
    """
    Execute REMOVE command to delete staged files after successful loading.

    Args:
        stage_name: Name of Snowflake stage to clean
        connection: Snowflake connector connection object

    Returns:
        dict with keys: files_removed, execution_time_sec, status, error_message
    """
    start = time.time()
    try:
        cs = connection.cursor()
        cs.execute(f"REMOVE @{stage_name}/")
        rows = cs.fetchall()
        cs.close()
        return {
            "files_removed": len(rows),
            "execution_time_sec": round(time.time() - start, 2),
            "status": "success",
            "error_message": None,
        }
    except Exception as e:
        return {
            "files_removed": 0,
            "execution_time_sec": round(time.time() - start, 2),
            "status": "error",
            "error_message": str(e),
        }
