from accounts_pipeline import get_accounts_data
from grants_pipeline import build_grants_table, build_funder_grants_table, build_recipients_table, build_recipient_grants_table
from supabase import create_client

def get_data(c_nums, api_key, supabase_key, supabase_url, skip_list=None):

    #get clean dataframe extracted from accounts pdfs
    accounts = get_accounts_data(c_nums, api_key, skip_list)

    #build grants and recipients tables from lists extracted from accounts
    grants = build_grants_table(accounts)
    funder_grants = build_funder_grants_table(grants)
    recipients = build_recipients_table(grants)

    #build recipient_grants tables
    recipient_grants = build_recipient_grants_table(recipients, grants, supabase_key, supabase_url)

    #drop temporary columns
    grants = grants.drop(columns=["charity_num", "recipient_name"], errors="ignore")

    #prepare funders data with most recent year only
    funders = accounts.copy()
    funders["year"] = funders["year"].astype(str)
    funders = funders.sort_values("year", ascending=False).drop_duplicates(subset=["registered_num"], keep="first")
    funders = funders[["registered_num", "objectives_activities", "achievements_performance", "grant_policy"]]

    #query existing funders to get their names
    supabase = create_client(supabase_url, supabase_key)
    registered_nums = funders["registered_num"].tolist()

    try:
        result = supabase.table("funders")\
            .select("registered_num, name")\
            .in_("registered_num", registered_nums)\
            .execute()

        if result.data:
            #create mapping of registered_num to name
            name_mapping = {row["registered_num"]: row["name"] for row in result.data}
            #add names to funders dataframe
            funders["name"] = funders["registered_num"].map(name_mapping)
            print(f"Fetched {len(name_mapping)} existing funder names from database")
    except Exception as e:
        print(f"Warning: Could not fetch existing funder names: {e}")

    #reorder columns to put name after registered_num
    funders = funders[["registered_num", "name", "objectives_activities", "achievements_performance", "grant_policy"]]

    return grants, funder_grants, recipient_grants, funders
