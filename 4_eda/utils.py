from supabase import create_client
import time
import pandas as pd

def get_table_from_supabase(url, key, table_name, batch_size=1000, delay=0.5, filter_recipients=False):
    """
    Fetches table data from Supabase
    """

    #create client instance
    supabase = create_client(url, key)

    all_data = []
    offset = 0

    while True:
        query = supabase.table(table_name).select("*")
        
        #only get actual recipients
        if filter_recipients and table_name == "recipients":
            query = query.eq("is_recipient", True)
        
        #batch imports
        response = query.limit(batch_size).offset(offset).execute()
        data = response.data
        if not data:
            break

        all_data.extend(data)
        offset += len(data)
    
        if len(data) < batch_size:
            break
            
        time.sleep(delay)

    df = pd.DataFrame(all_data)

    return df