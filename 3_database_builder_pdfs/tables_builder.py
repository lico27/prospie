from accounts_pipeline import get_accounts_data
from grants_pipeline import build_grants_table, build_recipients_table
def get_data(c_nums, api_key):

    #get clean dataframe extracted from accounts pdfs
    accounts = get_accounts_data(c_nums, api_key)

    #build grants and recipients tables from lists extracted from accounts
    grants = build_grants_table(accounts)
    recipients = build_recipients_table(grants)

    #build recipient_grants tables
    # recipient_grants = sync_grants_with_supabase(grants)

    return grants, recipients#, recipient_grants
