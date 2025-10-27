import pandas as pd
import os
from accounts_downloader import get_accounts_urls, download_accounts
from utils import ocr_accounts
from pdf_text_extractor import get_accounts_text

def get_accounts(c_nums):
    accounts = get_accounts_urls(c_nums)
    return accounts

def save_accounts(accounts):
    for i, row in accounts.iterrows():
        accounts_url = row["url"]
        registered_num = row["registered_num"]
        year = row["year_end"]

        #only download if url exists
        if accounts_url is not None:
            try:
                #download accounts
                save_path = f"accounts/{registered_num}_{year}.pdf"
                success = download_accounts(accounts_url, save_path)

                #add to df if successful
                if success:
                    accounts.at[i, "file_path"] = save_path
            except Exception as e:
                accounts.at[i, "file_path"] = None
        else:
            #no url available
            accounts.at[i, "file_path"] = None

    #loop through downloaded accounts and run ocr
    for i, row in accounts.iterrows():
        file_path = row.get("file_path")
        if file_path and os.path.exists(file_path):
            ocr_accounts(file_path)

    return accounts

def accounts_pipeline(c_nums):
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