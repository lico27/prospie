import traceback
import os
import pandas as pd
from dotenv import load_dotenv
from accounts_pipeline import get_accounts_data

#get key from env
load_dotenv()
anthropic_key = os.getenv("ANTHROPIC_KEY")

if __name__ == "__main__":
    try:
        #load charity numbers from sample
        # sample_file = os.path.join(os.path.dirname(__file__), "..", "1_sample_generator", "sample_charity_numbers.json")
        # with open(sample_file, 'r') as f:
        #     sample_data = json.load(f)
        # c_nums = sample_data["charity_numbers"]

        c_nums = ["1061180", "1157483"]

        accounts = get_accounts_data(c_nums, anthropic_key)

        pd.set_option('display.max_rows', None) #remove these after testing
        pd.set_option('display.max_columns', None)

        print(accounts.head())

        print("\n✓ Pipeline completed successfully!")

    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        traceback.print_exc()
        raise


