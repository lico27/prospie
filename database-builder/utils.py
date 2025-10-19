import pandas as pd

def clean_data(tables, title_cols, sentence_cols, int_cols):
    """
    Cleans data across multiple tables by standardizing formats and handling null values.

    Parameters
    ----------
    tables : list of DataFrames
        List of dataframes to clean
    title_cols : list of str
        Column names that should be converted to title case
    sentence_cols : list of str
        Column names that should be converted to sentence case
    int_cols : list of str
        Column names that should be converted to integers

    Returns
    -------
    list of DataFrames
        The cleaned dataframes in the same order as input
    """
    for i in range(len(tables)):
        #convert nans into json-readable nulls
        tables[i] = tables[i].where(pd.notnull(tables[i]), None)

        #change to title case for relevant columns
        for col in title_cols:
            if col in tables[i].columns:
                tables[i].loc[:, col] = tables[i][col].str.strip().str.title()

        #change to sentence case for relevant columns
        for col in sentence_cols:
            if col in tables[i].columns:
                tables[i].loc[:, col] = tables[i][col].str.strip().str.capitalize()

        #change to int for relevant columns
        for col in int_cols:
            if col in tables[i].columns:
                tables[i].loc[:, col] = tables[i][col].astype(int)

        #ensure financial figures are positive
        if "income" in tables[i].columns:
            tables[i].loc[tables[i]["income"] < 0, "income"] = None
        if "expenditure" in tables[i].columns:
            tables[i].loc[tables[i]["expenditure"] < 0, "expenditure"] = None

        #remove duplicates
        tables[i] = tables[i].drop_duplicates()

    return tables
