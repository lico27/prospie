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

def extract_classifications(row, section_cols, ukcat_df, areas_df):
    """
    Uses data from the Charity Classifications project to extract causes and beneficiaries, and Charity Commission data to match/extract areas.
    """

    #get existing extracted classifications
    existing_classes = list(row["extracted_class"]) if isinstance(row["extracted_class"], list) else []

    #concatenate sections
    sections = []
    for col in section_cols:
        if pd.notna(row[col]) and str(row[col]).strip():
            sections.append(str(row[col]))

    if not sections:
        return existing_classes

    text_to_search = " ".join(sections)

    matched_items = []

    #check against ukcat patterns
    for idx, ukcat_row in ukcat_df.iterrows():

        pattern = ukcat_row["Regular expression"]
        exclude_pattern = ukcat_row["Exclude regular expression"]

        if pd.isna(pattern) or not pattern:
            continue

        try:
            #check if patterns match
            if re.search(pattern, text_to_search, re.IGNORECASE):
                #check exclude patterns do not match
                if pd.notna(exclude_pattern) and exclude_pattern:
                    if re.search(exclude_pattern, text_to_search, re.IGNORECASE):
                        continue

                #add tag
                matched_items.append(ukcat_row["tag"])
        except re.error:
            continue

    #check against areas
    for idx, area_row in areas_df.iterrows():

        area_name = area_row["area_name"]

        if pd.isna(area_name) or not area_name:
            continue

        #handle partial matches
        pattern = r'\b' + re.escape(str(area_name)) + r'\b'

        try:
            if re.search(pattern, text_to_search, re.IGNORECASE):
                matched_items.append(area_name)
        except re.error:
            continue

    #combine with existing and return unique items
    all_classes = existing_classes + matched_items

    checked = set()
    unique_classes = []
    for item in all_classes:
        item_lower = str(item).lower()
        if item_lower not in checked:
            checked.add(item_lower)
            unique_classes.append(item)

    return unique_classes

