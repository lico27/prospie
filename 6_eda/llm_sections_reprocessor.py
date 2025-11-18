import os
from llm_sections_utils import get_last_pdf, extract_sections_with_llm, project_root

def reprocess_sections(registered_nums=None, limit=None):
    #configure
    MODEL = "claude-3-haiku-20240307"
    accounts_dir = os.path.join(project_root, "accounts")

    #get pdfs (latest one for each funder)
    funder_pdfs = get_last_pdf(accounts_dir)

    #filter to specific registered numbers if provided
    if registered_nums is not None:
        funder_pdfs = {k: v for k, v in funder_pdfs.items() if k in registered_nums}

    #get sections using LLM
    results_df = extract_sections_with_llm(funder_pdfs, limit=None, model=MODEL)

    return results_df

#call the function
llm_sections = reprocess_sections()

#save to csv
output_file = "llm_sections.csv"
llm_sections.to_csv(output_file, index=False)
print(f"{len(llm_sections)} PDFs reprocssed")

#view errors to inform rerun
errors = llm_sections["error"].notna().sum()
if errors > 0:
    print(f"{errors} funders had errors")
    error_nums = llm_sections[llm_sections["error"].notna()]["registered_num"].tolist()
    print(f"Failed: {error_nums}")