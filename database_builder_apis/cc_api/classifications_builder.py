import pandas as pd
from cc_api.transformers import transform_classification_table, transform_join_tables

def build_classifications_tables(df):

    """
    Takes Charity Commission data and explodes/normalizes the classification lists into columns.
    Drops unnecessary columns and rows.
    Builds classification and join tables ready to be piped to the database.
    """

    try:
        #explode classification lists and normalise into columns
        exploded_df_classifications = df.explode("classifications")
        classifications_df = pd.json_normalize(exploded_df_classifications["classifications"])

        #ensure required columns exist even if empty
        expected_columns = ["classification_type", "classification_desc", "classification_code"]
        for col in expected_columns:
            if col not in classifications_df.columns:
                classifications_df[col] = None

        #reset indexes and combine
        exploded_df_classifications = exploded_df_classifications.reset_index(drop=True)
        classifications_df = classifications_df.reset_index(drop=True)
        classifications_final = pd.concat([exploded_df_classifications, classifications_df], axis=1)

        #drop unnecessary columns and rows
        classifications_final = classifications_final.drop(columns=["name", "website", "activities", "objectives", "income", "expenditure", "classifications", "country_continent", "local_authority", "region"])
        classifications_final = classifications_final[classifications_final["classification_type"] != "How"]
    except Exception as e:
        print(f"Error processing classifications data: {e}")
        raise

    try:
        #build classification tables
        beneficiaries = transform_classification_table(classifications_final, "Who", "ben_id", "ben_name")
        causes = transform_classification_table(classifications_final, "What", "cause_id", "cause_name")

        #build join tables
        funder_causes = transform_join_tables(classifications_final, "What", "cause_id")
        funder_beneficiaries = transform_join_tables(classifications_final, "Who", "ben_id")
    except Exception as e:
        print(f"Error building classification tables: {e}")
        raise

    return beneficiaries, funder_beneficiaries, causes, funder_causes
