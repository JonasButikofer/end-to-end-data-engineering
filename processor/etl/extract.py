import pandas as pd
from sqlalchemy import create_engine
import os
from zoneinfo import ZoneInfo

def extract_table_data(table_name, since):
    """
    Extract rows from a Postgres table optionally filtered by a high watermark.
    Uses SQLAlchemy to avoid pandas connection warnings.
    """
    try:
        engine = create_engine(
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        )

        if since:
            query = f"SELECT * FROM {table_name} WHERE last_modified > %(since)s"
            df = pd.read_sql(query, con=engine, params={"since": since})
        else:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, con=engine)

        print(f"Found {len(df)} new records in {table_name}.")
        return df
    except Exception as e:
        print(f"[ERROR] Failed to extract from {table_name}: {e}")
        return pd.DataFrame()



def extract_chat_logs(since, collection):
    """
    Extract new chat logs from MongoDB since the last exported time.
    """
    try:
        if since:
            since = since.replace(tzinfo=ZoneInfo("America/Denver"))
            query = {"last_modified": {"$gt": since.isoformat()}}
        else:
            query = {}
        new_logs = list(collection.find(query))
        if not new_logs:
            return pd.DataFrame()
        df = pd.DataFrame(new_logs)
        df["_id"] = df["_id"].astype(str)
        df["last_modified"] = pd.to_datetime(df["last_modified"]).dt.tz_localize(None)
        print(f"Found {len(df)} new chat logs.")
        return df
    except Exception as e:
        print(f"[ERROR] Failed to extract chat logs: {e}")
        return None
