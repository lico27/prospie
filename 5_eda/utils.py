from supabase import create_client
import time
import pandas as pd

def get_table_from_supabase(url, key, table_name, batch_size=1000, delay=0.2, filter_recipients=False):
    """
    Fetches table data from Supabase with batching to avoid timeouts
    """

    #create client instance
    supabase = create_client(url, key)

    all_data = []
    offset = 0

    while True:
        query = supabase.table(table_name).select("*")

        #get only actual recipients
        if filter_recipients:
            query = query.eq("is_recipient", True)

        #batch imports
        try:
            response = query.limit(batch_size).offset(offset).execute()
            data = response.data
        except Exception as e:
            if "timeout" in str(e).lower() and batch_size > 10:
                return get_table_from_supabase(url, key, table_name, batch_size=batch_size // 2, delay=delay, filter_recipients=filter_recipients)
            raise

        if not data:
            break

        all_data.extend(data)
        offset += len(data)

        if len(data) < batch_size:
            break

        time.sleep(delay)

    df = pd.DataFrame(all_data)

    return df

def add_gbp_columns(x):
    """
    Adds a new column with currency formatted in GBP.
    """
    return f"£{x:,.2f}" if pd.notnull(x) else ""

def explode_lists(df, col):
    """
    Explodes a list column to create one row per list item.
    """
    return df.explode(col).dropna(subset=[col])
