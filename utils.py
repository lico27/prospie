import pandas as pd
from supabase import create_client
import time

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
        if "income" in tables[i].columns:
            tables[i].loc[tables[i]["income"] < 0, "income"] = None
        if "expenditure" in tables[i].columns:
            tables[i].loc[tables[i]["expenditure"] < 0, "expenditure"] = None

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
                    if isinstance(name, str) and name.startswith("The "):
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
