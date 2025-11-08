import pandas as pd
from supabase import create_client

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

def build_funder_grants_table(df):
    #build funder_grants join table from grants
    funder_grants = df[["charity_num", "grant_id"]].copy()
    funder_grants = funder_grants.rename(columns={"charity_num": "registered_num"})
    funder_grants = funder_grants.drop_duplicates()
    print(f"Created {len(funder_grants)} funder_grants records")

    return funder_grants

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

def build_recipient_grants_table(recipients, grants, key, url):
    
    supabase = create_client(url, key)

    #find existing pdf ids and batch
    all_pdf_ids = []
    page_size = 1000
    offset = 0

    while True:
        result = supabase.table("recipients")\
            .select("recipient_id")\
            .like("recipient_id", "PDF-%")\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        if not result.data:
            break
        
        all_pdf_ids.extend([r["recipient_id"] for r in result.data])
        offset += page_size
        
        if len(result.data) < page_size:
            break

    #find max existing pdf id and start counter
    max_counter = 0
    for pdf_id in all_pdf_ids:
        try:
            num_part = pdf_id.replace("PDF-", "")
            counter = int(num_part)
            if counter > max_counter:
                max_counter = counter
        except (ValueError, AttributeError):
            continue
    new_recipient_counter = max_counter + 1

    #get recipient names from database and batch
    recipient_names = [row["recipient_name"] for _, row in recipients.iterrows()]
    batch_size = 100
    existing_recipients = []

    for i in range(0, len(recipient_names), batch_size):
        batch_names = recipient_names[i:i+batch_size]

        try:
            result = supabase.table("recipients")\
                .select("recipient_id, recipient_name")\
                .in_("recipient_name", batch_names)\
                .execute()

            if result.data:
                existing_recipients.extend(result.data)
        except Exception as e:
            error_msg = str(e)
            if "statement timeout" in error_msg.lower():
                print(f"timeout on batch {i//batch_size + 1}")
            else:
                print(f"Error querying batch {i//batch_size + 1}: {e}")

    #get ids from names and create mapping
    id_from_name = {r["recipient_name"]: r["recipient_id"] for r in existing_recipients}

    #insert new recipients
    recipients_for_upsert = []

    for i, recipient_row in recipients.iterrows():
        recipient_name = recipient_row["recipient_name"]
        recipient_activities = recipient_row["recipient_activities"]

        if recipient_name in id_from_name:
            recipient_id = id_from_name[recipient_name]
        else:
            recipient_id = f"PDF-{new_recipient_counter:06d}"
            new_recipient_counter += 1
            id_from_name[recipient_name] = recipient_id

        #upsert all recipients to set is_recipient = True
        recipients_for_upsert.append({
            "recipient_id": recipient_id,
            "recipient_name": recipient_name,
            "recipient_activities": recipient_activities,
            "is_recipient": True
        })

    #upsert recipients to database
    if recipients_for_upsert:
        try:
            upsert_result = supabase.table("recipients").upsert(
                recipients_for_upsert,
                on_conflict="recipient_id"
            ).execute()
        except Exception as e:
            print(f"Error upserting recipients: {e}")

    print(f"Mapped {len(id_from_name)} recipient names to IDs")

    #build the join table
    recipient_grants_list = []

    for _, grant_row in grants.iterrows():
        grant_id = grant_row["grant_id"]
        recipient_name = grant_row["recipient_name"]
        
        #skip if empty/na
        if not recipient_name or not str(recipient_name).strip():
            continue
        
        #get actual id from mapping
        if recipient_name in id_from_name:
            recipient_id = id_from_name[recipient_name]
            
            recipient_grants_list.append({
                "grant_id": grant_id,
                "recipient_id": recipient_id
            })
        else:
            print(f"No recipient_id found for {recipient_name} in grant {grant_id}")

    #create dataframe
    recipient_grants = pd.DataFrame(recipient_grants_list)
    print(f"Created {len(recipient_grants)} recipient_grants records")
    print(f"Linked {len(grants)} grants to recipients")

    return recipient_grants