import pandas as pd
import os
import sys
from supabase import create_client
import time
from IPython.display import display, HTML
import re
import json
from sentence_transformers import SentenceTransformer, util

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

def extract_classifications(row, section_cols, ukcat_df, areas_df):
    """
    Uses data from the Charity Classifications project to extract causes and beneficiaries, and Charity Commission data to match/extract areas.
    """

    #get existing extracted classifications
    existing_classes = list(row["extracted_class"]) if isinstance(row["extracted_class"], list) else []

    #concatenate sections
    sections = []
    for col in section_cols:
        if pd.notna(row[col]) and str(row[col]).strip():
            sections.append(str(row[col]))

    if not sections:
        return existing_classes

    text_to_search = " ".join(sections)

    matched_items = []

    #check against ukcat patterns
    for idx, ukcat_row in ukcat_df.iterrows():

        pattern = ukcat_row["Regular expression"]
        exclude_pattern = ukcat_row["Exclude regular expression"]

        if pd.isna(pattern) or not pattern:
            continue

        try:
            #check if patterns match
            if re.search(pattern, text_to_search, re.IGNORECASE):
                #check exclude patterns do not match
                if pd.notna(exclude_pattern) and exclude_pattern:
                    if re.search(exclude_pattern, text_to_search, re.IGNORECASE):
                        continue

                #add tag
                matched_items.append(ukcat_row["tag"])
        except re.error:
            continue

    #check against areas
    for idx, area_row in areas_df.iterrows():

        area_name = area_row["area_name"]

        if pd.isna(area_name) or not area_name:
            continue

        #handle partial matches
        pattern = r'\b' + re.escape(str(area_name)) + r'\b'

        try:
            if re.search(pattern, text_to_search, re.IGNORECASE):
                matched_items.append(area_name)
        except re.error:
            continue

    #combine with existing and return unique items
    all_classes = existing_classes + matched_items

    checked = set()
    unique_classes = []
    for item in all_classes:
        item_lower = str(item).lower()
        if item_lower not in checked:
            checked.add(item_lower)
            unique_classes.append(item)

    return unique_classes

def get_id_from_name(area_name, df):
    """
    Searches for an area by name and returns its ID.
    """
    id_result = df[df["area_name"] == area_name]["area_id"].values
    return id_result[0] if len(id_result) > 0 else None

def get_name_from_id(area_id, df):
    """
    Searches for an area by ID and returns its name.
    """
    name_result = df[df["area_id"] == area_id]["area_name"].values
    return name_result[0] if len(name_result) > 0 else None

def get_granularity_weight(area_id, df):
    """
    Provides the weighting for an area based on the granularity of its level.
    """
    area_level = df[df["area_id"] == area_id]["area_level"].values[0]
    
    #england and wales areas
    if area_level == "local_authority":
        return 1.0
    elif area_level == "metropolitan_county":
        return 0.85
    elif area_level == "region":
        return 0.7
    #international areas
    elif area_level == "country":
        return 1.0
    elif area_level == "continent":
        return 0.7
    else:
        return 0.5

def get_descendants(area_id, df):
    """
    Compiles all descendants of a parent area.
    """
    descendants = set()
    areas_to_check = [area_id]
    
    while areas_to_check:
        current = areas_to_check.pop()
        children = df[df["parent_area_id"] == current]["child_area_id"].tolist()
        
        for child in children:
            if child not in descendants:
                descendants.add(child)
                areas_to_check.append(child)
    
    return descendants

def check_if_parent(parent_id, child_id, hierarchies_df):
    """
    Checks if an area is a parent of another.
    """
    descendants = get_descendants(parent_id, hierarchies_df)
    return child_id in descendants
 
def calculate_similarity_score(funder_embedding, user_embedding):
    """
    Calculates semantic similarity between user and funder using pre-computed embeddings.
    """
    
    #parse json   
    if isinstance(funder_embedding, str):
        funder_embedding = json.loads(funder_embedding)
    if isinstance(user_embedding, str):
        user_embedding = json.loads(user_embedding)
    
    #calculate cosine similarity
    score = util.cos_sim(funder_embedding, user_embedding).item()
    
    return max(0.0, score)
