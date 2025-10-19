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
        print(f"Skipping table '{table}' - DataFrame is empty (no data to upload)")
        return

    #make df into dictionaries to be readable by supabase
    records = df.to_dict("records")

    try:
        print(f"Attempting to upsert {len(records)} records to table: {table}")
        #pipe df to supabase
        response = (
            supabase.table(table)
            .upsert(records, on_conflict = unique_key)
            .execute()
        )
        print(f"✓ Successfully upserted {len(records)} records to {table}")
    except Exception as e:
        print(f"Error upserting to {table}: {e}")
        raise