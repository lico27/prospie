import pandas as pd
from supabase import create_client
import time
import re

def get_table_from_supabase(url, key, table_name, batch_size=1000, delay=0.2, filter_recipients=False):
    """
    Fetches table data from Supabase with batching to avoid timeouts
    """

    PRIMARY_KEYS = {
        "recipients": "recipient_id",
        "funders": "registered_num",
        "grants": "grant_id",
        "evaluation_pairs": "id",
        "beneficiaries": "ben_id",
        "causes": "cause_id",
        "areas": "area_id",
        "financials": "financials_id",
        "list_entries": "list_id",
        "funder_causes": "funder_causes_id",
        "funder_areas": "funder_areas_id",
        "funder_beneficiaries": "funder_ben_id",
        "funder_grants": "funder_grants_id",
        "funder_financials": "funder_fin_id",
        "funder_list": "funder_list_id",
        "recipient_grants": "recipient_grants_id",
        "recipient_areas": "recipient_areas_id",
        "recipient_beneficiaries": "recipient_ben_id",
        "recipient_causes": "recipient_cause_id",
        "embedding_pairs": "id",
        "logic_pairs": "id",
        "area_hierarchy": "parent_area_id"
    }

    #create client instance
    supabase = create_client(url, key)

    all_data = []
    offset = 0

    while True:
        query = supabase.table(table_name).select("*")

        #get only actual recipients
        if filter_recipients:
            query = query.eq("is_recipient", True)

        #order by primary key
        if table_name not in PRIMARY_KEYS:
            raise ValueError(f"Unknown table '{table_name}' - please add ordering column to PRIMARY_KEYS")

        query = query.order(PRIMARY_KEYS[table_name])

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
