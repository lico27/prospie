import pandas as pd
import os
from accounts_downloader import get_accounts_urls, download_accounts
from utils import ocr_accounts
from pdf_text_extractor import get_accounts_text, find_accounts_sections

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

    #loop through accounts to find objectives/activities and achievements/performance
    for i, row in accounts.iterrows():
        text = accounts.at[i, "accounts_text"]
        file_path = accounts.at[i, "file_path"]
        
        if text:
            print(f"Checking for objectives/activities and achievements in row {i}")
            has_obj, obj_text, has_achievement, achievement_text = find_accounts_sections(file_path, text)
            
            # Save text results
            accounts.at[i, "objectives_activities_text"] = obj_text
            accounts.at[i, "achievements_performance_text"] = achievement_text
            
            # Print results
            if has_obj and obj_text:
                print(f"  Objectives/activities found! Length: {len(obj_text)} characters")
            elif has_obj and not obj_text:
                print(f"  Objectives/activities heading found but text too short")
            
            if has_achievement and achievement_text:
                print(f"  Achievements/performance found! Length: {len(achievement_text)} characters")
            elif has_achievement and not achievement_text:
                print(f"  Achievements/performance heading found but text too short")
            
            if not has_obj and not has_achievement:
                print(f"  No sections found")
        else:
            accounts.at[i, "objectives_activities_text"] = None
            accounts.at[i, "achievements_performance_text"] = None

    return accounts