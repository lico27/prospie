import pandas as pd
from supabase import create_client

def pipe_to_supabase(df, table, unique_key, url, key, batch_size=1000):

    #create client instance
    supabase = create_client(url, key)

    #check if dataframe is empty
    if df.empty or len(df) == 0:
        return

    #parse unique key columns
    unique_cols = [col.strip() for col in unique_key.split(',')]

    #check for duplicates based on unique key
    duplicates_before = df.duplicated(subset=unique_cols, keep=False).sum()

    if duplicates_before > 0:
        #keep first occurrence of each duplicate
        df = df.drop_duplicates(subset=unique_cols, keep='first')

    #convert ints
    for col in df.columns:
        if df[col].dtype == 'Int64':
            df[col] = df[col].apply(lambda x: int(x) if pd.notna(x) else None)

    #make df into dictionaries to be readable by supabase
    records = df.to_dict("records")

    #batch upsert for large datasets
    total_records = len(records)

    try:
        for i in range(0, total_records, batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            #pipe batch to supabase
            supabase.table(table).upsert(batch, on_conflict = unique_key).execute()
            
        print(f"✓ Successfully upserted all {total_records} records to {table}")
    except Exception as e:
        print(f"✗ Error upserting to {table} at batch {batch_num}: {e}")
        raise