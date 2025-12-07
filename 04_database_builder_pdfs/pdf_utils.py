import re
import ocrmypdf
import pandas as pd
from supabase import create_client
from spellchecker import SpellChecker

def check_accounts(accounts_content, charity_num=None):

    prefix = f"[{charity_num}] " if charity_num else ""

    #check text is not unexpectedly short
    if len(accounts_content) < 100:
        return False

    #check proportion of unusual characters is not too high
    non_ascii = sum(1 for char in accounts_content if ord(char) > 127)
    non_ascii_pct = non_ascii / len(accounts_content)
    if non_ascii_pct > 0.45:
        return False

    #check years are present and from 2000 onwards
    year_pattern = r"\b20\d{2}\b"
    if not re.search(year_pattern, accounts_content):
        return False

    return True

def clean_ocr_text(text):
    """
    Runs spell check on OCRed text to try and catch misread characters.
    """
    spell = SpellChecker()
    
    lines = text.split('\n')
    corrected_lines = []

    for line in lines:
        words = line.split()
        corrected_words = []

        for word in words:
            if word.isalpha():
                correction = spell.correction(word.lower())
                if correction:
                    if word.isupper():
                        corrected_words.append(correction.upper())
                    elif word[0].isupper():
                        corrected_words.append(correction.capitalize())
                    else:
                        corrected_words.append(correction)
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)

        corrected_lines.append(' '.join(corrected_words))

    return '\n'.join(corrected_lines)

def ocr_accounts(pdf_path):
    """
    Runs OCR on downloaded accounts files to extract text into a format that can be read and analysed. 
    Resaves accounts files once text is extracted/converted.
    """
    try:
        ocrmypdf.ocr(
            pdf_path,
            pdf_path,
            skip_text=True,
            force_ocr=False,
            optimize=1,
            language="eng",
            progress_bar=False,
            invalidate_digital_signatures=True
        )
        return True
    except ocrmypdf.exceptions.PriorOcrFoundError:
        #skip if ocr not needed
        print(f"OCR not required: {pdf_path}")
        return True
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False
    
def extract_after_para(para_pattern, text):
    """
    Extracts content from text after a given paragraph reference.
    Checks for empty cells in CC17a form.
    """
    match = re.search(para_pattern, text, re.IGNORECASE)
    if not match:
        return None

    start = match.end()

    #check for empty cell
    next_content = text[start:start+100].strip()
    if next_content.startswith("Para ") or re.match(r"^[A-Z]*\d+[A-Z]*\s*$", next_content.split("\n")[0]):
        return None

    next_para = re.search(r"\nPara\s+\d+\.\d+", text[start:])
    
    if next_para:
        #estimate end of content
        tentative_end = start + next_para.start()
        chunk_before_para = text[max(start, tentative_end - 400):tentative_end]
        
        #use common patterns used in following sections
        desc_pattern = r"\n(Summary of|Policy on|Contribution made|Additional|Whether|Other)[^\n]*$"
        desc_match = re.search(desc_pattern, chunk_before_para, re.IGNORECASE)
        
        if desc_match:
            #use actual end if content found otherwise use estimate
            actual_end = max(start, tentative_end - 400) + desc_match.start()
            content = text[start:actual_end]
        else:
            content = text[start:tentative_end]
    else:
        #try and find heading if not found
        section_match = re.search(r"\n\n[A-Z][a-zA-Z\s]+\n", text[start:start+2000])
        if section_match:
            content = text[start:start + section_match.start()]
        else:
            #use reasonable estimate of length
            content = text[start:start + 1500]
    
    content = content.strip()
    return content if len(content) >= 20 else None

def find_next_section(text, start_pos):
        """
        Finds the next major section heading.
        """
        common_sections = [
            'Financial', 'Structure', 'Governance', 'Risk', 'Plans', 'Funding', 'Reserves',
            'Income', 'Expenditure', 'Trustees', 'Reference', 'Administrative', 'Statement',
            'Balance', 'Accounts', 'Notes', 'Independent', 'Auditor', 'Basis', 'Accounting',
            'Investment', 'Funds', 'Liabilities', 'Assets', 'Cashflow', 'Cash Flow',
            'Restricted', 'Unrestricted', 'Endowment', 'Resources', 'Reconciliation',
            'Related', 'Remuneration', 'Pension', 'Commitments', 'Contingent', 'Legal'
        ]

        #give headings options
        possible_words = '|'.join(common_sections)
        possible_sections = rf'(?:\n\s*\n\s*|\n)([A-Z][A-Za-z]+(?:\s+[A-Za-z]+)+|{possible_words})(?:\s*\n|\s*$)'

        match = re.search(possible_sections, text[start_pos:], re.IGNORECASE)
        if match:
            return start_pos + match.start()

        return None

def clean_tables(df, cols):

    #clean strings
    for col in cols:
        if col in df.columns:
            df.loc[:, col] = (df[col]
                                    .fillna("")
                                    .astype(str)
                                    .str.replace('\n', ' ', regex=False)
                                    .str.strip()
                                    .str.upper())
            df.loc[df[col] == "", col] = None

    #convert year to int if present
    if "year" in df.columns:
        df.loc[:, "year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    return df

def clean_dictionaries(list_of_dicts):
    if not list_of_dicts or not isinstance(list_of_dicts, list):
        return list_of_dicts

    cleaned_dicts = []
    for item in list_of_dicts:
        if isinstance(item, dict):
            new_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    #convert numbers to floats and clean/uppercase strings
                    try:
                        new_item[key] = float(value)
                    except (ValueError, TypeError):
                        new_item[key] = value.replace('\n', ' ').strip().upper()
                elif isinstance(value, (int, float)):
                    new_item[key] = float(value)
                else:
                    new_item[key] = value

            #ensure financial figures are positive
            if "amount" in new_item and isinstance(new_item["amount"], (int, float)):
                if new_item["amount"] < 0:
                    new_item["amount"] = None

            #remove 'the' from organisation names
            for key in ["name", "funder_name", "recipient_name"]:
                if key in new_item and isinstance(new_item[key], str) and new_item[key].startswith("THE "):
                    new_item[key] = new_item[key][4:]

            cleaned_dicts.append(new_item)
        else:
            cleaned_dicts.append(item)
    return cleaned_dicts

def get_360_funders(supabase_url, supabase_key):
    """
    Queries Supabase to find funders who report to 360Giving, in order to skip them in API grant extraction.
    """
    try:
        supabase = create_client(supabase_url, supabase_key)
        response = supabase.table("funder_grants").select("registered_num").execute()

        if response.data:
            #get unique charity numbers
            skip_list = list(set([row["registered_num"] for row in response.data]))
            return skip_list
        return []
    except Exception as e:
        print(f"Warning: Could not query 360Giving funders from Supabase: {e}")
        print("Proceeding without skip list...")
        return []