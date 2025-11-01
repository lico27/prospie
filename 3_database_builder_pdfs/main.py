import traceback
import os
import pandas as pd
import json
from dotenv import load_dotenv
from tables_builder import get_data

#get key from env
load_dotenv()
anthropic_key = os.getenv("ANTHROPIC_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if __name__ == "__main__":
    try:
        #load charity numbers from sample
        sample_file = os.path.join(os.path.dirname(__file__), "..", "1_sample_generator", "sample_charity_numbers.json")
        with open(sample_file, 'r') as f:
            sample_data = json.load(f)
        c_nums = sample_data["charity_numbers"][55:59]

        # c_nums = ["1061180", "1157483"]

        grants, recipients, recipient_grants = get_data(c_nums, anthropic_key, supabase_key, supabase_url)

        # pd.set_option('display.max_rows', None) #remove these after testing
        # pd.set_option('display.max_columns', None)

        # print(accounts.head())

        print("\n✓ Pipeline completed successfully!")

    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        traceback.print_exc()
        raise


