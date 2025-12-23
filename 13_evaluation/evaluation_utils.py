import pandas as pd
import os
import sys
from supabase import create_client
import time
from IPython.display import display, HTML

project_root = os.path.abspath('..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from utils import build_relationship_cols

def get_recipients_by_id(url, key, recipient_ids, batch_size=1000):
    """
    Fetches specific recipients from supabase and builds the df with their join tables.
    """

    supabase = create_client(url, key)

    #convert series to list
    if hasattr(recipient_ids, "tolist"):
        recipient_ids = recipient_ids.tolist()

    #get recipients
    all_recipients = []
    for i in range(0, len(recipient_ids), batch_size):
        batch_ids = recipient_ids[i:i + batch_size]
        response = supabase.table("recipients").select("*").in_("recipient_id", batch_ids).execute()
        all_recipients.extend(response.data)
        time.sleep(0.1)

    recipients_df = pd.DataFrame(all_recipients)

    #get join tables
    join_tables_data = {}
    for table_name in ["recipient_areas", "recipient_causes", "recipient_beneficiaries"]:
        data = []
        for i in range(0, len(recipient_ids), batch_size):
            batch_ids = recipient_ids[i:i + batch_size]
            response = supabase.table(table_name).select("*").in_("recipient_id", batch_ids).execute()
            data.extend(response.data)
            time.sleep(0.1)
        join_tables_data[table_name] = pd.DataFrame(data)

    areas = pd.DataFrame(supabase.table("areas").select("*").execute().data)
    causes = pd.DataFrame(supabase.table("causes").select("*").execute().data)
    beneficiaries = pd.DataFrame(supabase.table("beneficiaries").select("*").execute().data)

    #define table relationships
    recipient_rels = [
        {
            "join_table": join_tables_data["recipient_areas"],
            "lookup_table": areas,
            "key": "area_id",
            "value_col": "area_name",
            "result_col": "recipient_areas"
        },
        {
            "join_table": join_tables_data["recipient_causes"],
            "lookup_table": causes,
            "key": "cause_id",
            "value_col": "cause_name",
            "result_col": "recipient_causes"
        },
        {
            "join_table": join_tables_data["recipient_beneficiaries"],
            "lookup_table": beneficiaries,
            "key": "ben_id",
            "value_col": "ben_name",
            "result_col": "recipient_beneficiaries"
        }
    ]

    #add relationship columns
    recipients_df = build_relationship_cols(recipients_df, "recipient_id", recipient_rels)

    return recipients_df

def format_tests(idx, row, result):
    """
    Makes simple cards to display results of test.
    """

    #design html
    html = f"""
    <div style="background: #1e1e1e; padding: 5px; margin: 5px 0; font-family: sans-serif; color: #d4d4d4;">
        <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px; color: #4ec9b0;">
            #{idx + 1}: {row['name']} & {row['user_name']}
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; font-size: 13px;">
            <div><span style="color: #808080;">prospie score:</span> {result * 100:.2f}%</div>
        </div>

    </div>
    """

    display(HTML(html))
