import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client

#get keys from env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

#create client instance
supabase = create_client(url, key)

def pipe_to_supabase(df, table, unique_key):

    #check if dataframe is empty
    if df.empty or len(df) == 0:
        return

    #parse unique key columns
    unique_cols = [col.strip() for col in unique_key.split(',')]

    #check for duplicates based on unique key
    original_count = len(df)
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

    try:
        #pipe df to supabase
        response = (
            supabase.table(table)
            .upsert(records, on_conflict = unique_key)
            .execute()
        )
        print(f"✓ Successfully upserted {len(records)} records to {table}")
    except Exception as e:
        print(f"✗ Error upserting to {table}: {e}")
        raise