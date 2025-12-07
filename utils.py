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
        if table_name == "recipients":
            query = query.order("recipient_id")
        elif table_name == "funders":
            query = query.order("registered_num")
        elif table_name == "grants":
            query = query.order("grant_id")
        elif table_name == "evaluation_pairs":
            query = query.order("id")
        elif table_name == "beneficiaries":
            query = query.order("ben_id")
        elif table_name == "causes":
            query = query.order("cause_id")
        elif table_name == "areas":
            query = query.order("area_id")
        elif table_name == "financials":
            query = query.order("financials_id")
        elif table_name == "list_entries":
            query = query.order("list_id")
        elif table_name == "funder_causes":
            query = query.order("funder_causes_id")
        elif table_name == "funder_areas":
            query = query.order("funder_areas_id")
        elif table_name == "funder_beneficiaries":
            query = query.order("funder_ben_id")
        elif table_name == "funder_grants":
            query = query.order("funder_grants_id")
        elif table_name == "funder_financials":
            query = query.order("funder_fin_id")
        elif table_name == "funder_list":
            query = query.order("funder_list_id")
        elif table_name == "recipient_grants":
            query = query.order("recipient_grants_id")
        elif table_name == "recipient_areas":
            query = query.order("recipient_areas_id")
        elif table_name == "recipient_beneficiaries":
            query = query.order("recipient_ben_id")
        elif table_name == "recipient_causes":
            query = query.order("recipient_cause_id")
        elif table_name == "embedding_pairs":
            query = query.order("id")
        elif table_name == "logic_pairs":
            query = query.order("id")
        elif table_name == "area_hierarchy":
            query = query.order("parent_area_id")
        else:
            raise ValueError(f"Unknown table '{table_name}' - please add ordering column to get_table_from_supabase()")

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