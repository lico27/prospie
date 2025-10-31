import json
import os
import traceback
from tables_builder import get_data
from data_importer import pipe_to_supabase

if __name__ == "__main__":
    try:
        #load charity numbers from sample
        sample_file = os.path.join(os.path.dirname(__file__), "..", "1_sample_generator", "sample_charity_numbers.json")
        with open(sample_file, 'r') as f:
            sample_data = json.load(f)
        c_nums = sample_data["charity_numbers"]

        #get data
        funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas, grants, funder_grants, recipients, recipient_grants, recipient_areas, potential_recipients = get_data(c_nums)

        #dictionary to hold tables and their keys
        tables = {
            "funders": (funders, "registered_num"),
            "beneficiaries": (beneficiaries, "ben_id"),
            "causes": (causes, "cause_id"),
            "areas": (areas, "area_id"),
            "grants": (grants, "grant_id"),
            "recipients": (recipients, "recipient_id"),
            #"recipients": (potential_recipients, "recipient_id"),
            "funder_beneficiaries": (funder_beneficiaries, "registered_num,ben_id"),
            "funder_causes": (funder_causes, "registered_num,cause_id"),
            "funder_areas": (funder_areas, "registered_num,area_id"),
            "funder_grants": (funder_grants, "registered_num,grant_id"),
            "recipient_grants": (recipient_grants, "recipient_id,grant_id"),
            "recipient_areas": (recipient_areas, "recipient_id,area_id")
        }

        #pipe data to supabase
        for table_name, (df, unique_key) in tables.items():
            pipe_to_supabase(df, table_name, unique_key)

        print("\n✓ Pipeline completed successfully!")

    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        traceback.print_exc()
        raise

    