import json
import os
import traceback
from accounts_pipeline import get_accounts, save_accounts


if __name__ == "__main__":
    try:
        #load charity numbers from sample
        # sample_file = os.path.join(os.path.dirname(__file__), "..", "1_sample_generator", "sample_charity_numbers.json")
        # with open(sample_file, 'r') as f:
        #     sample_data = json.load(f)
        # c_nums = sample_data["charity_numbers"]

        c_nums = ["1061180", "1157483"]

        #download and save accounts locally
        accounts = get_accounts(c_nums)
        accounts = save_accounts(accounts)

        print("\n✓ Pipeline completed successfully!")

    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        traceback.print_exc()
        raise


