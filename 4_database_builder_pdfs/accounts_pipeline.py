import os
from accounts_downloader import get_accounts, save_accounts
from pdf_text_extractor import get_accounts_text, get_accounts_sections, get_previous_grants
from utils import clean_tables, clean_dictionaries

def get_accounts_data(c_nums, api_key):
    
    #download and save accounts locally
    accounts = get_accounts(c_nums)
    accounts = save_accounts(accounts)

    #loop through accounts to extract text
    for i, row in accounts.iterrows():
        file_path = row.get("file_path")
        if file_path and os.path.exists(file_path):
            print(f"Extracting text from: {file_path}")
            get_accounts_text(file_path, accounts, i)
        else:
            accounts.at[i, "accounts_text"] = None
    
    #extract important sections from each document
    accounts = get_accounts_sections(accounts)

    #extract information about previous grants declared by the funder
    accounts = get_previous_grants(api_key, accounts)

    #tidy and clean dataframe ready to be imported
    accounts = accounts.rename(columns={"year_end": "year",
                                        "objectives_activities_text": "objectives_activities",
                                        "achievements_performance_text": "achievements_performance",
                                        "grant_policy_text": "grant_policy"}
                                        ).drop(columns=["accounts_text", "file_path", "accounts_accessed"])
    
    accounts = clean_tables(accounts, ["objectives_activities", "achievements_performance", "grant_policy"])

    for i, row in accounts.iterrows():
        accounts.at[i, "individual_grants"] = clean_dictionaries(row["individual_grants"])
        accounts.at[i, "category_totals"] = clean_dictionaries(row["category_totals"])

    return accounts