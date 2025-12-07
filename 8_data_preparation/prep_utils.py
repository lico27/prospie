import pandas as pd
import spacy
import re

def extract_areas(row, section_cols, nlp):
    """
    Identifies areas and extracts from funder sections.
    """

    #concatenate sections and convert to titlecase
    sections = []
    for col in section_cols:
        if pd.notna(row[col]) and str(row[col]).strip():
            sections.append(str(row[col]).title())
    
    if not sections:
        return []
    
    text_to_search = " ".join(sections)
    
    #run ner
    doc = nlp(text_to_search)
    areas = []
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC", "FAC"]:
            areas.append(ent.text)
    
    #return unique areas
    checked = set()
    unique_areas = []
    for loc in areas:
        if loc not in checked:
            checked.add(loc)
            unique_areas.append(loc)
    
    return unique_areas

def extract_causes_from_ukcat(row, section_cols, ukcat_df):
    """
    Uses data from the Charity Classifications project to extract causes and beneficiaries from funder sections.
    """
    #concatenate sections
    sections = []
    for col in section_cols:
        if pd.notna(row[col]) and str(row[col]).strip():
            sections.append(str(row[col]))

    if not sections:
        return []

    text_to_search = " ".join(sections)

    #check against ukcat patterns
    matched_categories = []

    for idx, ukcat_row in ukcat_df.iterrows():

        pattern = ukcat_row["Regular expression"]
        exclude_pattern = ukcat_row["Exclude regular expression"]

        if pd.isna(pattern) or not pattern:
            continue

        try:
            #checkk if patterns match
            if re.search(pattern, text_to_search, re.IGNORECASE):
                #check exclude patterns do not match
                if pd.notna(exclude_pattern) and exclude_pattern:
                    if re.search(exclude_pattern, text_to_search, re.IGNORECASE):
                        continue

                #add tag
                matched_categories.append(ukcat_row["tag"])
        except re.error:
            continue

    return list(set(matched_categories))

def extract_causes(row, section_cols, ukcat_df):
    """
    Uses data from the Charity Classifications project to extract causes and beneficiaries from funder sections.
    """

    #get existing extracted classifications
    existing_class = list(row["extracted_class"]) if isinstance(row["extracted_class"], list) else []

    #concatenate sections
    sections = []
    for col in section_cols:
        if pd.notna(row[col]) and str(row[col]).strip():
            sections.append(str(row[col]))

    if not sections:
        return existing_class

    text_to_search = " ".join(sections)

    #check against ukcat patterns
    matched_categories = []

    for idx, ukcat_row in ukcat_df.iterrows():

        pattern = ukcat_row["Regular expression"]
        exclude_pattern = ukcat_row["Exclude regular expression"]

        if pd.isna(pattern) or not pattern:
            continue

        try:
            #checkk if patterns match
            if re.search(pattern, text_to_search, re.IGNORECASE):
                #check exclude patterns do not match
                if pd.notna(exclude_pattern) and exclude_pattern:
                    if re.search(exclude_pattern, text_to_search, re.IGNORECASE):
                        continue

                #add tag
                matched_categories.append(ukcat_row["tag"])
        except re.error:
            continue
    
    #return unique causes/beneficiaries
    checked = set()
    unique_causes = []
    for cause in matched_categories:
        if cause not in checked:
            checked.add(cause)
            unique_causes.append(cause)
    
    return unique_causes
