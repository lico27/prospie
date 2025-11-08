import json
import pandas as pd
import os
import sys

#add project root to path for utils import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import clean_data

def get_all_charities():
    #load json file and filter for registered charities
    registered_charities = []
    json_path = os.path.join(os.path.dirname(__file__), "publicextract.charity.json")
    with open(json_path, "r", encoding="utf-8-sig") as f:
        first_line = f.readline().strip()

        #process each line
        for line in f:
            if line.strip() == "]":
                break

            #remove whitespace and commas
            line = line.strip()
            if line.startswith(","):
                line = line[1:]
            if line.endswith(","):
                line = line[:-1]

            #skip empty lines
            if not line:
                continue

            try:
                #parse json object
                charity = json.loads(line)

                #filter to registered charities only
                if (charity.get("linked_charity_number") == 0 and
                    charity.get("charity_registration_status") == "Registered"):
                    registered_charities.append(charity)
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {e}")
                continue

    #create dataframe and rename columns
    potential_recipients = pd.DataFrame(registered_charities)
    potential_recipients = potential_recipients[["registered_charity_number", "charity_name", "charity_activities"]].rename(columns={
        "registered_charity_number": "recipient_id",
        "charity_name": "recipient_name",
        "charity_activities": "recipient_activities"
    })

    #add boolean check
    potential_recipients["is_recipient"] = False

    #clean data
    cleaned_tables = clean_data([potential_recipients], ["recipient_name", "recipient_activities"], [])
    potential_recipients = cleaned_tables[0]

    return potential_recipients

def get_recipient_classifications(all_recipient_ids):
    """
    Gets data from Charity Commission json extract for recipients and their classifications.
    """

    #get classification json file
    classifications = []
    json_path = os.path.join(os.path.dirname(__file__), "publicextract.charity_classification.json")

    with open(json_path, "r", encoding="utf-8-sig") as f:
        first_line = f.readline().strip()

        #process each line
        for line in f:
            if line.strip() == "]":
                break

            #remove whitespace and commas
            line = line.strip()
            if line.startswith(","):
                line = line[1:]
            if line.endswith(","):
                line = line[:-1]

            #skip empty lines
            if not line:
                continue

            try:
                #parse json object
                classification = json.loads(line)

                #filter to registered charities that exist in recipients table
                if (classification.get("linked_charity_number") == 0 and
                    str(classification.get("registered_charity_number")) in all_recipient_ids):
                    classifications.append(classification)
            except json.JSONDecodeError as e:
                print(f"Error parsing classification line: {e}")
                continue

    #create dataframe
    classifications_df = pd.DataFrame(classifications)

    #rename columns to match expected format
    classifications_df = classifications_df.rename(columns={
        "registered_charity_number": "recipient_id",
        "classification_code": "classification_code",
        "classification_type": "classification_type",
        "classification_description": "classification_desc"
    })

    #filter out how
    classifications_df = classifications_df[classifications_df["classification_type"] != "How"]

    #convert recipient_id to string for consistency
    classifications_df["recipient_id"] = classifications_df["recipient_id"].astype(str)

    #build beneficiaries table
    beneficiaries = (classifications_df[classifications_df["classification_type"] == "Who"]
        .drop_duplicates(subset=["classification_desc"], keep="first")
        [["classification_code", "classification_desc"]]
        .rename(columns={"classification_code": "ben_id", "classification_desc": "ben_name"})
    )

    #build causes table
    causes = (classifications_df[classifications_df["classification_type"] == "What"]
        .drop_duplicates(subset=["classification_desc"], keep="first")
        [["classification_code", "classification_desc"]]
        .rename(columns={"classification_code": "cause_id", "classification_desc": "cause_name"})
    )

    #build recipient_beneficiaries join table
    recipient_beneficiaries = (classifications_df[classifications_df["classification_type"] == "Who"]
        [["recipient_id", "classification_code"]]
        .rename(columns={"classification_code": "ben_id"})
        .drop_duplicates()
    )

    #build recipient_causes join table
    recipient_causes = (classifications_df[classifications_df["classification_type"] == "What"]
        [["recipient_id", "classification_code"]]
        .rename(columns={"classification_code": "cause_id"})
        .drop_duplicates()
    )

    return beneficiaries, causes, recipient_beneficiaries, recipient_causes
