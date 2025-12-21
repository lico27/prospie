import re
import pandas as pd
import json
from sentence_transformers import SentenceTransformer, util
from IPython.display import display, HTML

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

def format_score_test(idx, row, result):
    """
    Makes simple cards to display results of test.
    """
    #unpack score elements
    (is_sbf, is_nua, is_on_list, list_reasoning,
    existing_relationship, num_grants, relationship, areas_score,
    areas_reasoning, beneficiaries_score, beneficiaries_reasoning,
    causes_score, causes_reasoning, text_similarity_score,
    keyword_similarity_score, keyword_strong_matches, keyword_reasoning, keyword_gets_bonus,
    name_score_rp, name_rp_reasoning, grants_rp_score, grants_rp_reasoning,
    recipients_rp_score, recipients_rp_reasoning, sbf_penalty, keywords_bonus,
    time_lapsed, relationship_bonus, last_grant_year, areas_rp_bonus, areas_rp_reasoning,
    keywords_rp_bonus, keywords_rp_reasoning, lv_penalty) = result

    #design html
    html = f"""
    <div style="background: #1e1e1e; padding: 15px; margin: 10px 0; font-family: sans-serif; color: #d4d4d4;">
        <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #4ec9b0;">
            #{idx}: {row['name']} & {row['user_name']}
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; font-size: 13px;">
            <div><span style="color: #808080;">SBF:</span> {'❌' if is_sbf else '✅'}</div>
            <div><span style="color: #808080;">NUA:</span> {'❌' if is_nua else '✅'}</div>
            <div><span style="color: #808080;">List:</span> {'❌' if is_on_list else '✅'}</div>
            <div><span style="color: #808080;">Relationship:</span> {num_grants} grants</div>
            <div><span style="color: #808080;">Areas:</span> {areas_score:.2f}</div>
            <div><span style="color: #808080;">Beneficiaries:</span> {beneficiaries_score:.2f}</div>
            <div><span style="color: #808080;">Causes:</span> {causes_score:.2f}</div>
            <div><span style="color: #808080;">Text:</span> {text_similarity_score:.2f}</div>
            <div><span style="color: #808080;">Keywords:</span> {keyword_similarity_score:.2f} {'🎁' if keyword_gets_bonus else ''}</div>
            <div><span style="color: #808080;">Name (RP):</span> {name_score_rp:.2f}</div>
            <div><span style="color: #808080;">Grants (RP):</span> {grants_rp_score:.2f}</div>
            <div><span style="color: #808080;">Recipients (RP):</span> {recipients_rp_score:.2f}</div>
        </div>
        
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #333; font-size: 12px; color: #ce9178;">
            <span style="color: #808080;">Multipliers:</span>
            SBF: {sbf_penalty:.2f} | KW: {keywords_bonus:.2f} | Rel: {relationship_bonus:.2f} | 
            Areas: {areas_rp_bonus:.2f} | KW(RP): {keywords_rp_bonus:.2f} | LV: {lv_penalty:.2f}
        </div>
    </div>
    """

    display(HTML(html))