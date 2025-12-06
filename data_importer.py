import pandas as pd
import numpy as np
import json
import time
from supabase import create_client

def pipe_to_supabase(df, table, unique_key, url, key, batch_size=1000, delay=0.5):

    #create client instance
    supabase = create_client(url, key)

    #check if dataframe is empty
    if df.empty or len(df) == 0:
        return

    #parse unique key columns
    unique_cols = [col.strip() for col in unique_key.split(",")]

    #check for duplicates based on unique key
    duplicates_before = df.duplicated(subset=unique_cols, keep=False).sum()

    if duplicates_before > 0:
        #keep first occurrence of each duplicate
        df = df.drop_duplicates(subset=unique_cols, keep="first")

    #convert ints
    for col in df.columns:
        if df[col].dtype == "Int64":
            df[col] = df[col].apply(lambda x: int(x) if pd.notna(x) else None)

    #handle json non-compliance
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32']:
            #replace inf and -inf with None
            df[col] = df[col].replace([np.inf, -np.inf], None)
            #replace NaN with None
            df[col] = df[col].apply(lambda x: None if pd.isna(x) or (isinstance(x, float) and not np.isfinite(x)) else x)
    df = df.where(pd.notna(df), None)

    #make df into dictionaries to be readable by supabase
    records = df.to_dict("records")

    #additional json validation
    for record in records:
        for key, value in record.items():
            if isinstance(value, float):
                if np.isnan(value) or np.isinf(value):
                    record[key] = None

    #batch upsert for large datasets
    total_records = len(records)

    try:
        for i in range(0, total_records, batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            try:
                json.dumps(batch)
            except (ValueError, TypeError) as json_err:
                print(f"JSON validation failed for batch {batch_num}: {json_err}")
                print(f"First record in batch: {batch[0]}")
                raise

            #pipe batch to supabase
            supabase.table(table).upsert(batch, on_conflict = unique_key).execute()

            #add delay
            if i + batch_size < total_records:
                time.sleep(delay)

        print(f"Successfully upserted all {total_records} records to {table}")
    except Exception as e:
        print(f"✗ Error upserting to {table} at batch {batch_num}: {e}")
        raise