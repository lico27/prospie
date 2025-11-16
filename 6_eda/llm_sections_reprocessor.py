import os
from llm_sections_utils import get_last_pdf, extract_sections_with_llm, project_root

def reprocess_sections(limit=None):
    #configure
    MODEL = "claude-3-haiku-20240307"
    accounts_dir = os.path.join(project_root, "accounts")

    #get pdfs (latest one for each funder)
    funder_pdfs = get_last_pdf(accounts_dir)

    #get sections using LLM
    results_df = extract_sections_with_llm(funder_pdfs, limit=None, model=MODEL)

    return results_df