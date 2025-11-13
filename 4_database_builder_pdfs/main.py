import traceback
import os
import sys
import pandas as pd
import json
from dotenv import load_dotenv
from tables_builder import get_data
from utils import get_360_funders

#add project root to path for data_importer import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_importer import pipe_to_supabase

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
        c_nums = sample_data["charity_numbers"]

        #get list of funders with 360giving data
        skip_list = get_360_funders(supabase_url, supabase_key)

        grants, funder_grants, recipient_grants, funders = get_data(c_nums, anthropic_key, supabase_key, supabase_url, skip_list)

        #dictionary to hold tables and their keys
        tables = {
            "grants": (grants, "grant_id"),
            "funder_grants": (funder_grants, "registered_num,grant_id"),
            "recipient_grants": (recipient_grants, "recipient_id,grant_id"),
            "funders": (funders, "registered_num"),
        }

        #pipe data to supabase
        for table_name, (df, unique_key) in tables.items():
            pipe_to_supabase(df, table_name, unique_key, supabase_url, supabase_key)

        print("Pipeline complete!")

    except Exception as e:
        print(f"Pipeline failed with error: {e}")
        traceback.print_exc()
        raise


