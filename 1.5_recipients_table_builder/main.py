import os
import sys
from dotenv import load_dotenv
from all_charities_pipeline import get_all_charities

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

        #send data to supabase
        pipe_to_supabase(all_charities, "recipients", "recipient_id", supabase_url, supabase_key)

        print("Recipients table setup complete")

    except Exception as e:
        print(f"Setup failed with error: {e}")
        raise
