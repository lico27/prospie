import pdfplumber
import fitz
import re
from utils import check_accounts
from sections_extractor import find_sections_by_sorp, find_sections_by_regex

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
        if text and "(cid:" not in text[:1000] and check_accounts(text):
            accounts_df.at[index, "accounts_text"] = text
            return
        
        #backup attempt for more complex files
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        #validate again before saving
        if check_accounts(text):
            accounts_df.at[index, "accounts_text"] = text
        else:
            print(f"Text failed validation for {pdf_path}")
            accounts_df.at[index, "accounts_text"] = None
        
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        accounts_df.at[index, "accounts_text"] = None

def find_accounts_sections(df):
    """
    Checks accounts for objectives & activities, achievements & performance, and grant policy sections - or variously worded/formatted versions thereof.
    First checks for tables containing SORP references for accounts that use Charity Commission's CC17a form, then uses regex if SORP references not found.
    Processes each row in the dataframe and saves results.
    """

    #loop through accounts to find objectives/activities, achievements/performance, and grant policy
    for i, row in df.iterrows():
        text = df.at[i, "accounts_text"]

        if text:
            # Try SORP first
            has_obj, obj_text, has_achievement, achievement_text, has_policy, policy_text = find_sections_by_sorp(text)

            # Use regex as fallback for any sections not found by SORP
            if not has_obj or not has_achievement or not has_policy:
                regex_has_obj, regex_obj_text, regex_has_achievement, regex_achievement_text, regex_has_policy, regex_policy_text = find_sections_by_regex(text)

                # Only use regex results if SORP didn't find them
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