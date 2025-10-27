import json
import traceback
from accounts_pipeline import accounts_pipeline


if __name__ == "__main__":
    try:
        #load charity numbers from sample
        # sample_file = os.path.join(os.path.dirname(__file__), "..", "1_sample_generator", "sample_charity_numbers.json")
        # with open(sample_file, 'r') as f:
        #     sample_data = json.load(f)
        # c_nums = sample_data["charity_numbers"]

        c_nums = ["1061180", "1157483"]

        accounts = accounts_pipeline(c_nums)

        print(accounts.head())

        print("\n✓ Pipeline completed successfully!")

    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        traceback.print_exc()
        raise


