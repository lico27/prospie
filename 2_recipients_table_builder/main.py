import os
import sys
from dotenv import load_dotenv
from all_charities_pipeline import get_all_charities, get_recipient_classifications

#add project root to path for data_importer import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_importer import pipe_to_supabase

#get keys from env
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if __name__ == "__main__":

    try:
        #get all charities from cc as potential recipients
        all_charities = get_all_charities()

        #get recipient classifications
        all_recipient_ids = set(all_charities["recipient_id"].astype(str))
        beneficiaries, causes, recipient_beneficiaries, recipient_causes = get_recipient_classifications(all_recipient_ids)

        #dictionary to hold tables and their keys
        tables = {
            "recipients": (all_charities, "recipient_id"),
            "beneficiaries": (beneficiaries, "ben_id"),
            "causes": (causes, "cause_id"),
            "recipient_beneficiaries": (recipient_beneficiaries, "recipient_id,ben_id"),
            "recipient_causes": (recipient_causes, "recipient_id,cause_id")
        }

        #pipe data to supabase
        for table_name, (df, unique_key) in tables.items():
            pipe_to_supabase(df, table_name, unique_key, supabase_url, supabase_key)

        print("Recipients tables uploaded successfully")

    except Exception as e:
        print(f"Setup failed with error: {e}")
        raise
