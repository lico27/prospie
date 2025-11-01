import pandas as pd

def build_grants_table(df):
    grants_list = []

    for i, row in df.iterrows():
        individual_grants = row.get("individual_grants", [])
        year = row.get("year")
        registered_num = row.get("registered_num")
        
        if individual_grants and isinstance(individual_grants, list):
            grant_counter = 1
            
            for grant in individual_grants:
                #create grant_id from year, num and counter
                grant_id = f"{year}_{registered_num}_{grant_counter}"
                
                grants_list.append({
                    "grant_id": grant_id,
                    "grant_title": None,
                    "grant_desc": None,
                    "amount": grant.get("amount"),
                    "year": year,
                    #temporary to track and build recipients later
                    "charity_num": registered_num,
                    "recipient_name": grant.get("recipient_name")
                })
                grant_counter += 1

    #create dataframe
    grants = pd.DataFrame(grants_list)
    print(f"Created {len(grants)} grant records")

    return grants

def build_recipients_table(df):
    #get unique recipient names and filter for nones
    unique_recipients = df["recipient_name"].unique()
    unique_recipients = [name for name in unique_recipients if name and str(name).strip()]

    recipients_list = []
    for recipient_name in unique_recipients:
        recipients_list.append({
            "recipient_name": recipient_name.strip(),
            "recipient_activities": None
        })

    #create dataframe 
    recipients = pd.DataFrame(recipients_list)
    print(f"Created {len(recipients)} recipient records")

    return recipients

def sync_grants_with_supabase(df):
    pass