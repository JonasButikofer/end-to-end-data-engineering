# metadata/watermark.py
from datetime import datetime

def get_watermark(source_id, pg_conn):
    """
    Retrieve the last export timestamp for a given source from Postgres metadata.
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT last_export FROM processor_metadata WHERE id = %s", (source_id,))
            result = cur.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"[WARN] Could not fetch watermark for {source_id}: {e}")
        return None

def update_watermark(source_id, timestamp, pg_conn):
    """
    Update or insert the last export timestamp for a given source in Postgres metadata.
    """
    try:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        with pg_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO processor_metadata (id, last_export)
                VALUES (%s, %s)
                ON CONFLICT (id)
                DO UPDATE SET last_export = EXCLUDED.last_export;
            """, (source_id, timestamp))
            pg_conn.commit()
    except Exception as e:
        print(f"[ERROR] Failed to update watermark for {source_id}: {e}")
