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

        #remove null bytes and other invalid characters from strings
        for col in tables[i].columns:
            if tables[i][col].dtype == "object":
                def clean_string(x):
                    if isinstance(x, str):
                        x = x.replace("\x00", "")
                        x = "".join(char for char in x if ord(char) >= 32 or char in ["\n", "\t", "\r"])
                        return x
                    return x
                tables[i][col] = tables[i][col].apply(clean_string)

        #change to title case for relevant columns
        for col in title_cols:
            if col in tables[i].columns:
                tables[i].loc[:, col] = tables[i][col].fillna("").astype(str).str.strip().str.title()
                tables[i].loc[tables[i][col] == "", col] = None

        #change to sentence case for relevant columns
        for col in sentence_cols:
            if col in tables[i].columns:
                tables[i].loc[:, col] = tables[i][col].fillna("").astype(str).str.strip().str.capitalize()
                tables[i].loc[tables[i][col] == "", col] = None

        #change to int for relevant columns
        for col in int_cols:
            if col in tables[i].columns:
                tables[i].loc[:, col] = pd.to_numeric(tables[i][col], errors="coerce").astype("Int64")

        #ensure financial figures are positive
        if "income" in tables[i].columns:
            tables[i].loc[tables[i]["income"] < 0, "income"] = None
        if "expenditure" in tables[i].columns:
            tables[i].loc[tables[i]["expenditure"] < 0, "expenditure"] = None

        #make sure websites are formatted correctly
        if "website" in tables[i].columns:
            def format_website(url):
                if url and not url.startswith(("http://", "https://")):
                    return "https://" + url
                return url
            tables[i].loc[tables[i]["website"].notnull(), "website"] = tables[i].loc[tables[i]["website"].notnull(), "website"].apply(format_website)

        #remove 'the' from organisation names
        for col in ["funder_name", "recipient_name"]:
            if col in tables[i].columns:
                def remove_leading_the(name):
                    if isinstance(name, str) and name.startswith("The "):
                        return name[4:]
                    return name
                tables[i].loc[:, col] = tables[i][col].apply(remove_leading_the)

        #remove duplicates
        tables[i] = tables[i].drop_duplicates()

    return tables
