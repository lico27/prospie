import pandas as pd
from cc_api.client import call_financial_history_api
from cc_api.transformers import transform_financials_df, transform_financials_long, transform_financials_join

def build_financials_tables(c_nums):

    try:
        #call api and make df
        financial_data = call_financial_history_api(c_nums)
        df = transform_financials_df(financial_data)

        #build financials table and join table
        financials = transform_financials_long(df)
        funder_financials = transform_financials_join(df)

    except Exception as e:
        print(f"Error building financials tables: {e}")
        raise

    return financials, funder_financials
