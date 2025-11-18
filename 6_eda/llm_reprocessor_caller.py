import os
from llm_sections_reprocessor import reprocess_sections

#call the function
llm_sections = reprocess_sections()

#save to csv
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "llm_sections.csv")
llm_sections.to_csv(output_file, index=False)
print(f"{len(llm_sections)} PDFs reprocssed")

#view errors to inform rerun
errors = llm_sections["error"].notna().sum()
if errors > 0:
    print(f"{errors} funders had errors")
    error_nums = llm_sections[llm_sections["error"].notna()]["registered_num"].tolist()
    print(f"Failed: {error_nums}")
