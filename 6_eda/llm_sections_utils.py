import os
import sys
import pandas as pd
from pathlib import Path
import importlib.util
from dotenv import load_dotenv
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
root_utils_path = os.path.join(project_root, "utils.py")
spec = importlib.util.spec_from_file_location("root_utils", root_utils_path)
root_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_utils)
get_table_from_supabase = root_utils.get_table_from_supabase
sys.path.insert(0, os.path.join(project_root, "4_database_builder_pdfs"))
from pdf_text_extractor import get_accounts_text
from llm_sections_extractor import extract_sections

#get key from env
load_dotenv()
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

def get_last_pdf(folder):
    """
    Gets the last pdf for each funder in the accounts folder.
    """
    accounts_path = Path(folder)

    if not accounts_path.exists():
        raise FileNotFoundError(f"Accounts folder not found: {folder}")

    funder_pdfs = {}

    #scan all pdfs and parse filename
    for pdf_file in accounts_path.glob("*.pdf"):
        filename = pdf_file.stem
        parts = filename.split("_")
        if len(parts) != 2:
            print(f"Skipping pdf with unexpected format: {pdf_file.name}")
            continue

        registered_num = parts[0]
        year = parts[1]

        #keep only the last accounts for each funder
        if registered_num not in funder_pdfs:
            funder_pdfs[registered_num] = (year, str(pdf_file))
        else:
            existing_year, _ = funder_pdfs[registered_num]
            if year > existing_year:
                funder_pdfs[registered_num] = (year, str(pdf_file))

    return funder_pdfs

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from PDF.
    """
    #store in df
    df = pd.DataFrame([{"file_path": pdf_path}])

    try:
        get_accounts_text(pdf_path, df, 0)
        text = df.at[0, "accounts_text"]
        return text if pd.notna(text) else None
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def extract_sections_with_llm(funder_pdfs, model="claude-3-haiku-20240307", limit=None):
    """
    Processes PDFs then extracts sections using LLM.
    """
    results = []
    processed_count = 0

    #limit if necessary
    items = list(funder_pdfs.items())
    if limit:
        items = items[:limit]

    total = len(items)
    print(f"\nProcessing {total} pdfs")

    for i, (registered_num, (year, pdf_path)) in enumerate(items, 1):
        print(f"[{i}/{total}] {registered_num} ({year})...", end=" ")

        #extract text
        pdf_text = extract_text_from_pdf(pdf_path)

        if not pdf_text:
            print("SKIPPED (text extraction failed)")
            results.append({
                "registered_num": registered_num,
                "year_processed": year,
                "objectives_activities": None,
                "achievements_performance": None,
                "grant_policy": None,
                "error": "Text extraction failed"
            })
            continue

        #use llm to extract sections
        try:
            sections = extract_sections(ANTHROPIC_KEY, pdf_text, model=model)

            results.append({
                "registered_num": registered_num,
                "year_processed": year,
                "objectives_activities": sections["objectives_activities"],
                "achievements_performance": sections["achievements_performance"],
                "grant_policy": sections["grant_policy"],
                "error": None
            })

            processed_count += 1

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "registered_num": registered_num,
                "year_processed": year,
                "objectives_activities": None,
                "achievements_performance": None,
                "grant_policy": None,
                "error": str(e)
            })

        #limit rate
        time.sleep(1.2)

    print(f"Processed {processed_count} funders successfully.")
    return pd.DataFrame(results)

