import os
import sys
import traceback
import glob
from dotenv import load_dotenv
from csv_pipeline import get_list_data

#add project root to path for data_importer import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_importer import pipe_to_supabase

#get keys from env
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if __name__ == "__main__":
    try:
        #find most recent csv file matching pattern "the-list-*.csv"
        csv_dir = os.path.dirname(__file__)
        csv_files = glob.glob(os.path.join(csv_dir, "the-list-*.csv"))

        if not csv_files:
            raise FileNotFoundError("No CSV files found matching pattern 'the-list-*.csv'")

        #get most recent csv
        csv_file = sorted(csv_files)[-1]

        #get data from csv
        list_entries, funder_list = get_list_data(csv_file, supabase_url, supabase_key)

        #dictionary to hold tables and their keys
        tables = {
            "list_entries": (list_entries, "list_id"),
            "funder_list": (funder_list, "registered_num,list_id")
        }

        #pipe data to supabase
        for table_name, (df, unique_key) in tables.items():
            pipe_to_supabase(df, table_name, unique_key, supabase_url, supabase_key)

        #change bool to true for funders on the list
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)

        if not funder_list.empty:
            funders_on_list = funder_list["registered_num"].unique().tolist()

            for registered_num in funders_on_list:
                try:
                    supabase.table("funders").update({"is_on_list": True}).eq("registered_num", registered_num).execute()
                except Exception as e:
                    print(f"Warning: Could not update is_on_list for {registered_num}: {e}")

        print("Pipeline completed successfully!")

    except Exception as e:
        print(f"Pipeline failed with error: {e}")
        traceback.print_exc()
        raise
