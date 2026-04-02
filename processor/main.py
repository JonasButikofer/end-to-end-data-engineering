# Entry point: main.py
from utils.env_loader import load_environment
from datetime import datetime, timezone
import time
import os

load_environment()

INTERVAL = int(os.getenv("PROCESSOR_INTERVAL_SEC", "0"))
MAX_RUNTIME = int(os.getenv("PROCESSOR_MAX_RUNTIME_SEC", "3600"))
ENABLE_COPY_INTO = os.getenv("PROCESSOR_ENABLE_COPY_INTO", "true").lower() == "true"
ENABLE_CLEANUP = os.getenv("PROCESSOR_ENABLE_CLEANUP", "true").lower() == "true"


# The extract section below is complete. Your job: implement the
# COPY INTO and cleanup orchestration in the TODO section (Task 2).
def run_once():
    from etl.extract import extract_table_data, extract_chat_logs
    from etl.load import upload_dataframe_to_stage, copy_stage_to_table, clean_stage
    from utils.connections import get_postgres_connection, get_snowflake_connection, get_mongo_collection
    from utils.watermark import get_watermark, update_watermark

    cycle_start = time.time()
    run_time = datetime.now(timezone.utc)
    print(f"\n{'='*60}")
    print(f"[{run_time.isoformat()}] CYCLE START")
    print(f"{'='*60}")

    pg_conn = get_postgres_connection()

    # --- Extract from PostgreSQL source: orders ---
    watermark_orders = get_watermark("orders_source", pg_conn)
    df_orders = extract_table_data("orders", since=watermark_orders)

    if not df_orders.empty:
        upload_dataframe_to_stage(df_orders, "orders", "orders_stage", run_time, file_format="csv")
        new_wm = df_orders["last_modified"].max()
        update_watermark("orders_source", new_wm, pg_conn)

    # --- Extract from PostgreSQL source: order_details ---
    watermark_details = get_watermark("order_details_source", pg_conn)
    df_details = extract_table_data("order_details", since=watermark_details)

    if not df_details.empty:
        upload_dataframe_to_stage(df_details, "order_details", "order_details_stage", run_time, file_format="csv")
        new_wm = df_details["last_modified"].max()
        update_watermark("order_details_source", new_wm, pg_conn)

    # --- Extract from MongoDB source: chat_logs ---
    mongo_collection = get_mongo_collection()
    watermark_chat = get_watermark("chat_source", pg_conn)
    df_chat = extract_chat_logs(since=watermark_chat, collection=mongo_collection)

    if df_chat is not None and not df_chat.empty:
        upload_dataframe_to_stage(df_chat, "chat_logs", "chat_stage", run_time, file_format="json")
        new_wm = df_chat["last_modified"].max()
        update_watermark("chat_source", new_wm, pg_conn)

    pg_conn.close()

    # --- Load stages to raw tables ---
    if ENABLE_COPY_INTO:
        sf_conn = get_snowflake_connection()

        stages = [
            ("orders_stage", "orders_raw", "CSV"),
            ("order_details_stage", "order_details_raw", "CSV"),
            ("chat_stage", "chat_logs_raw", "JSON"),
        ]

        copy_results = []
        for stage_name, table_name, fmt in stages:
            result = copy_stage_to_table(stage_name, table_name, fmt, connection=sf_conn)
            copy_results.append((stage_name, result))
            if result["status"] == "success":
                print(f"COPY {stage_name} -> {table_name}: {result['rows_copied']} rows copied, {result['rows_skipped']} skipped ({result['execution_time_sec']}s)")
            else:
                print(f"COPY {stage_name} -> {table_name} FAILED: {result['error_message']}")

        if ENABLE_CLEANUP:
            for stage_name, result in copy_results:
                if result["status"] == "success":
                    clean = clean_stage(stage_name, connection=sf_conn)
                    if clean["status"] == "success":
                        print(f"Cleaning {stage_name}: {clean['files_removed']} files removed ({clean['execution_time_sec']}s)")
                    else:
                        print(f"Cleaning {stage_name} FAILED: {clean['error_message']}")

        sf_conn.close()

    cycle_time = round(time.time() - cycle_start, 2)
    print(f"\n[{datetime.now(timezone.utc).isoformat()}] CYCLE COMPLETE ({cycle_time} sec)")
    print(f"{'='*60}\n")


def main():
    if INTERVAL > 0:
        start_time = time.time()
        runtime_msg = f", max runtime: {MAX_RUNTIME}s" if MAX_RUNTIME > 0 else ""
        print(f"Running processor every {INTERVAL} seconds{runtime_msg}...")
        while True:
            run_once()
            if MAX_RUNTIME > 0 and (time.time() - start_time) >= MAX_RUNTIME:
                print(f"\nMax runtime of {MAX_RUNTIME}s reached. Shutting down.")
                break
            time.sleep(INTERVAL)
    else:
        run_once()


if __name__ == "__main__":
    main()
