import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client
from all_charities_pipeline import get_recipient_objectives

#add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import clean_text

#get keys from env
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

def get_existing_recipients():
    """
    Gets existing recipient ids from supabase
    """
    supabase = create_client(supabase_url, supabase_key)
    all_recipient_ids = set()
    page_size = 1000
    offset = 0

    while True:
        response = supabase.table("recipients").select("recipient_id").range(offset, offset + page_size - 1).execute()

        if not response.data:
            break

        recipient_ids_batch = set(str(row["recipient_id"]) for row in response.data)
        all_recipient_ids.update(recipient_ids_batch)

        if len(response.data) < page_size:
            break

        offset += page_size

    print(f"Got {len(all_recipient_ids)} recipients")

    return all_recipient_ids

def import_objectives(objectives_dict):
    """
    Adds objectives to existing recipients in supabase.
    """
    supabase = create_client(supabase_url, supabase_key)
    total = len(objectives_dict)
    success_count = 0
    error_count = 0
    batch_size = 100
    items = list(objectives_dict.items())

    #batch process updates
    for i in range(0, total, batch_size):
        batch_end = min(i + batch_size, total)
        batch_items = items[i:batch_end]

        for recipient_id, objectives in batch_items:
            try:
                response = supabase.table("recipients").update({
                    "recipient_objectives": clean_text(objectives)
                }).eq("recipient_id", recipient_id).execute()

                success_count += 1

            except Exception as e:
                print(f"Error updating recipient {recipient_id}: {e}")
                error_count += 1

        #show progress
        print(f"Processed {batch_end}/{total} recipients (success: {success_count}, errors: {error_count})...")

    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    try:
        #get ids and objectives data
        all_recipient_ids = get_existing_recipients()
        objectives_dict = get_recipient_objectives(all_recipient_ids)

        #pipe back to supabase
        import_objectives(objectives_dict)

        print("Objectives successfully added to recipients")

    except Exception as e:
        print(f"Update failed with error: {e}")
        raise
