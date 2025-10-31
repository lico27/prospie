import json
import pandas as pd
import os
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

    #clean data
    cleaned_tables = clean_data([potential_recipients], ["recipient_name", "recipient_activities"], [])
    potential_recipients = cleaned_tables[0]

    return potential_recipients
