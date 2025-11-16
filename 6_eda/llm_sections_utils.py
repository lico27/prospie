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

#get keys from env
load_dotenv()
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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
