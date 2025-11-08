import pdfplumber
import fitz
import pandas as pd
import time
from utils import check_accounts, clean_ocr_text
from sections_and_grants_extractor import find_sections_by_sorp, find_sections_by_regex, find_grants

def get_accounts_text(pdf_path, accounts_df, index):
    """ 
    Extracts text from an accounts file and saves it to the dataframe.
    Uses a two-step process to deal with accounts containing CID characters.
    """
    try:
        #try fitz for speed
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()

        #check for validity of text
        if text and "(cid:" not in text[:1000]:
            #apply spell checking to clean OCR errors
            text = clean_ocr_text(text)
            if check_accounts(text):
                accounts_df.at[index, "accounts_text"] = text
                return

        #backup attempt for more complex files
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        #apply spell checking to clean ocr errors
        if text:
            text = clean_ocr_text(text)

        #validate again before saving
        if check_accounts(text):
            accounts_df.at[index, "accounts_text"] = text
        else:
            print(f"Text failed validation for {pdf_path}")
            accounts_df.at[index, "accounts_text"] = None
        
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        accounts_df.at[index, "accounts_text"] = None

def get_accounts_sections(df):
    """
    Checks accounts for objectives & activities, achievements & performance, and grant policy sections - or variously worded/formatted versions thereof.
    First checks for tables containing SORP references for accounts that use Charity Commission's CC17a form, then uses regex if SORP references not found.
    Processes each row in the dataframe and saves results.
    """

    #loop through accounts to find objectives/activities, achievements/performance, and grant policy
    for i, row in df.iterrows():
        text = df.at[i, "accounts_text"]

        if text:
            #look for sorp references
            has_obj, obj_text, has_achievement, achievement_text, has_policy, policy_text = find_sections_by_sorp(text)

            #use regex where sorp is not present
            if not has_obj or not has_achievement or not has_policy:
                regex_has_obj, regex_obj_text, regex_has_achievement, regex_achievement_text, regex_has_policy, regex_policy_text = find_sections_by_regex(text)
                if not has_obj:
                    has_obj = regex_has_obj
                    obj_text = regex_obj_text
                if not has_achievement:
                    has_achievement = regex_has_achievement
                    achievement_text = regex_achievement_text
                if not has_policy:
                    has_policy = regex_has_policy
                    policy_text = regex_policy_text

            #save results
            df.at[i, "objectives_activities_text"] = obj_text
            df.at[i, "achievements_performance_text"] = achievement_text
            df.at[i, "grant_policy_text"] = policy_text
        else:
            df.at[i, "objectives_activities_text"] = None
            df.at[i, "achievements_performance_text"] = None
            df.at[i, "grant_policy_text"] = None

    return df

def get_previous_grants(api_key, df, skip_list=None):

    #make new columns if needed
    if "individual_grants" not in df.columns:
        df["individual_grants"] = pd.Series(dtype="object")
    if "category_totals" not in df.columns:
        df["category_totals"] = pd.Series(dtype="object")

    #get grants info from each set of accounts
    total_accounts = len(df)
    processed = 0
    if skip_list is None:
        skip_list = []

    for i, row in df.iterrows():
        text = df.at[i, "accounts_text"]
        registered_num = row.get("registered_num")

        #skip api call if funder already in 360giving data
        if registered_num in skip_list:
            print(f"  Skipping grant extraction for {registered_num} (already has 360Giving data)")
            df.at[i, "individual_grants"] = []
            df.at[i, "category_totals"] = []
            processed += 1
            continue

        if text:
            print(f"  Extracting grants {processed + 1}/{total_accounts}...")
            grants_data = find_grants(api_key, text)
            df.at[i, "individual_grants"] = grants_data.get("individual_grants", [])
            df.at[i, "category_totals"] = grants_data.get("category_totals", [])

            #limit requests
            if processed < total_accounts - 1:
                time.sleep(1.3)
        else:
            df.at[i, "individual_grants"] = []
            df.at[i, "category_totals"] = []

        processed += 1

    return df


