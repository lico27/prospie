import pandas as pd
from supabase import create_client
from datetime import datetime

def read_csv_data(csv_file):
    """
    Reads CSV file and extracts data from The List.
    """
    df = pd.read_csv(csv_file)

    #combine text into one column
    df["list_info"] = df.apply(
        lambda row: f"{row['Description']}\n\n{row['Additional Details']}"
        if pd.notna(row['Additional Details']) and str(row['Additional Details']).strip()
        else str(row['Description']),
        axis=1
    )

    #clean
    df["registered_num"] = df["Charity Number"].astype(str).str.strip()
    df["list_type"] = df["Change Type"].str.strip()
    df["list_date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

    #filter to valid registered nums (england/wales only)
    df = df[
        df["registered_num"].notna() &
        (df["registered_num"] != "") &
        (df["registered_num"] != "nan") &
        df["registered_num"].str[0].str.isdigit()
    ]

    return df[["registered_num", "list_type", "list_date", "list_info"]]

def build_list_table(df, supabase_url, supabase_key):
    """
    Builds table to upsert The List entries.
    """

    supabase = create_client(supabase_url, supabase_key)

    #get unique list entries
    list_entries = df[["list_type", "list_date", "list_info"]].drop_duplicates().reset_index(drop=True)
    list_entries["list_date"] = list_entries["list_date"].dt.strftime("%Y-%m-%d")

    try:
        #fetch all existing list entries from database
        result = supabase.table("list_entries").select("list_id, list_type, list_date, list_info").execute()

        if result.data and len(result.data) > 0:
            existing_entries = pd.DataFrame(result.data)
            max_list_id = existing_entries["list_id"].max()
            next_list_id = max_list_id + 1
        else:
            existing_entries = pd.DataFrame(columns=["list_id", "list_type", "list_date", "list_info"])
            next_list_id = 1
    except Exception as e:
        print(f"ERROR: Could not fetch existing list entries from database: {e}")
        raise

    #merge with existing entries to reuse ids for duplicates
    list_entries = list_entries.merge(
        existing_entries,
        on=["list_type", "list_date", "list_info"],
        how="left"
    )

    #assign new id if not found
    new_entries_mask = list_entries["list_id"].isna()
    num_new_entries = new_entries_mask.sum()
    list_entries.loc[new_entries_mask, "list_id"] = range(next_list_id, next_list_id + num_new_entries)
    list_entries["list_id"] = list_entries["list_id"].astype(int)

    return list_entries

def build_funder_list_table(df, list_entries, supabase_url, supabase_key):
    """
    Builds funder_list join table linking funders to list entries.
    Only includes funders that exist in the funders table.
    """

    df = df.copy()
    df["list_date"] = df["list_date"].dt.strftime("%Y-%m-%d")

    #merge original data with list_entries to get list_ids
    funder_list = df.merge(
        list_entries,
        on=["list_type", "list_date", "list_info"],
        how="left"
    )[["registered_num", "list_id"]].drop_duplicates()

    #fetch existing funders from database to validate foreign keys
    supabase = create_client(supabase_url, supabase_key)

    try:
        result = supabase.table("funders").select("registered_num").execute()
        existing_funders = set(row["registered_num"] for row in result.data)

        #filter to only include funders that exist in the database
        initial_count = len(funder_list)
        funder_list = funder_list[funder_list["registered_num"].isin(existing_funders)]
        filtered_count = initial_count - len(funder_list)

        if filtered_count > 0:
            print(f"Warning: Filtered out {filtered_count} funder_list records for charities not in funders table")

        print(f"Created {len(funder_list)} funder_list records")

    except Exception as e:
        print(f"ERROR: Could not fetch existing funders from database: {e}")
        raise

    return funder_list

def get_list_data(csv_file, supabase_url, supabase_key):
    """
    Calls functions to build list tables.
    """
    df = read_csv_data(csv_file)
    list_entries = build_list_table(df, supabase_url, supabase_key)

    #build join table
    funder_list = build_funder_list_table(df, list_entries, supabase_url, supabase_key)

    return list_entries, funder_list
