import pandas as pd
from supabase import create_client
import time
import re

def clean_data(tables, upper_cols, int_cols):
    """
    Cleans data 
    """
    for i in range(len(tables)):
        #convert nans into json-readable nulls
        tables[i] = tables[i].where(pd.notnull(tables[i]), None)

        #remove null bytes and other invalid characters from strings
        for col in tables[i].columns:
            if tables[i][col].dtype == "object":
                def clean_string(x):
                    if isinstance(x, str):
                        x = x.replace("\x00", "")
                        x = "".join(char for char in x if ord(char) >= 32 or char in ["\n", "\t", "\r"])
                        return x
                    return x
                tables[i][col] = tables[i][col].apply(clean_string)

        #change to uppercase for relevant columns
        for col in upper_cols:
            if col in tables[i].columns:
                tables[i].loc[:, col] = tables[i][col].fillna("").astype(str).str.strip().str.upper()
                tables[i].loc[tables[i][col] == "", col] = None

        #change to int for relevant columns
        for col in int_cols:
            if col in tables[i].columns:
                tables[i].loc[:, col] = pd.to_numeric(tables[i][col], errors="coerce").astype("Int64")

        #ensure financial figures are positive
        if "income_latest" in tables[i].columns:
            tables[i].loc[tables[i]["income_latest"] < 0, "income_latest"] = None
        if "expenditure_latest" in tables[i].columns:
            tables[i].loc[tables[i]["expenditure_latest"] < 0, "expenditure_latest"] = None

        #make sure websites are formatted correctly
        if "website" in tables[i].columns:
            def format_website(url):
                if url and not url.startswith(("http://", "https://")):
                    return "https://" + url
                return url
            tables[i].loc[tables[i]["website"].notnull(), "website"] = tables[i].loc[tables[i]["website"].notnull(), "website"].apply(format_website)

        #remove 'the' from organisation names
        for col in ["name", "funder_name", "recipient_name"]:
            if col in tables[i].columns:
                def remove_leading_the(name):
                    if isinstance(name, str) and name.startswith("THE "):
                        return name[4:]
                    return name
                tables[i].loc[:, col] = tables[i][col].apply(remove_leading_the)

        #remove duplicates
        tables[i] = tables[i].drop_duplicates()

    return tables

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

def clean_text(text):
    """
    Cleans a string.
    """
    if not isinstance(text, str):
        return text

    #remove null bytes and prolem characters
    text = text.replace("\x00", "")
    text = "".join(char for char in text if ord(char) >= 32 or char in ["\n", "\t", "\r"])
    text = re.sub(r"^[^a-zA-Z0-9]+", "", text)

    #strip spaces and make uppercase
    text = text.strip().upper()

    return text if text else None

def build_relationship_cols(base_df, join_key, relationships):
    """
    Merges and groups data to build relationship columns between join/main tabls.
    """
    result_df = base_df.copy()

    for rel in relationships:
        grouped = rel["join_table"].merge(rel["lookup_table"], on=rel["key"])
        grouped = grouped.groupby(join_key)[rel["value_col"]].apply(list).reset_index()
        grouped.columns = [join_key, rel["result_col"]]
        result_df = result_df.merge(grouped, on=join_key, how="left")

        #replace nan values with empty lists
        result_df[rel["result_col"]] = result_df[rel["result_col"]].apply(
            lambda x: x if isinstance(x, list) else []
        )

    return result_df

def build_financial_history(base_df, join_key, funder_financials, financials_table):
    """
    Builds income and expenditure history columns for funders dataframe.
    """
    result_df = base_df.copy()

    #get full financial records and separate into income and expenditure
    financial_history = funder_financials.merge(financials_table, on="financials_id")
    income_history = financial_history[financial_history["financials_type"] == "income"]
    expenditure_history = financial_history[financial_history["financials_type"] == "expenditure"]

    #make financials dicts
    income_by_funder = income_history.groupby(join_key).apply(
        lambda x: dict(zip(x["financials_year"], x["financials_value"]))
    ).reset_index()
    income_by_funder.columns = [join_key, "income_history"]

    expenditure_by_funder = expenditure_history.groupby(join_key).apply(
        lambda x: dict(zip(x["financials_year"], x["financials_value"]))
    ).reset_index()
    expenditure_by_funder.columns = [join_key, "expenditure_history"]

    #merge and replace nan values
    result_df = result_df.merge(income_by_funder, on=join_key, how="left")
    result_df = result_df.merge(expenditure_by_funder, on=join_key, how="left")
    result_df["income_history"] = result_df["income_history"].apply(lambda x: x if isinstance(x, dict) else {})
    result_df["expenditure_history"] = result_df["expenditure_history"].apply(lambda x: x if isinstance(x, dict) else {})

    return result_df

def add_grant_statistics(base_df, join_key, funder_grants, grants_table):
    """
    Adds grant statistics columns to the funders dataframe.
    """
    result_df = base_df.copy()

    grants_stats = funder_grants.merge(grants_table, on="grant_id")
    grants_agg = grants_stats.groupby(join_key).agg({
        "grant_id": "count",
        "amount": ["sum", "mean", "median"]
    }).reset_index()
    grants_agg.columns = [join_key, "num_grants", "total_given", "avg_grant", "median_grant"]

    result_df = result_df.merge(grants_agg, on=join_key, how="left")
    result_df["num_grants"] = result_df["num_grants"].astype("Int64")

    return result_df

def extract_areas(row, section_cols, nlp):
    """
    Identifies areas and extracts from funder sections.
    """

    #concatenate sections and convert to titlecase
    sections = []
    for col in section_cols:
        if pd.notna(row[col]) and str(row[col]).strip():
            sections.append(str(row[col]).title())
    
    if not sections:
        return []
    
    text_to_search = " ".join(sections)
    
    #run ner
    doc = nlp(text_to_search)
    areas = []
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC", "FAC"]:
            areas.append(ent.text)
    
    #return unique areas
    checked = set()
    unique_areas = []
    for loc in areas:
        if loc not in checked:
            checked.add(loc)
            unique_areas.append(loc)
    
    return unique_areas

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

