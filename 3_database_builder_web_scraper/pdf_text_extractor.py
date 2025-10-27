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

def find_accounts_sections(pdf_path, text):
    """
    Checks accounts for objectives & activities and achievements & performance sections - or variously worded/formatted versions thereof.
    First checks for tables containing SORP references for accounts that use Charity Commission's CC17a form, then uses regex if SORP references not found.
    Returns boolean confirmation of the required sections, and their text if it exists.
    """
    if not text:
        return False, None, False, None
    


    #get required sections trying sorp first
    has_obj, obj_text, has_achievement, achievement_text = find_sections_by_sorp(text)
    if not has_obj or not has_achievement:
        regex_has_obj, regex_obj_text, regex_has_achievement, regex_achievement_text = find_sections_by_regex(text)
        if not has_obj:
            has_obj = regex_has_obj
            obj_text = regex_obj_text
        if not has_achievement:
            has_achievement = regex_has_achievement
            achievement_text = regex_achievement_text

    return has_obj, obj_text, has_achievement, achievement_text