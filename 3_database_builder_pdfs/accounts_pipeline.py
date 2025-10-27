import os
from accounts_downloader import get_accounts, save_accounts
from pdf_text_extractor import get_accounts_text, get_accounts_sections

def get_accounts_data(c_nums):
    
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
   
    return accounts