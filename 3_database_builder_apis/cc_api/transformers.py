import pandas as pd

def transform_classification_table(df, classification_type, id_col, name_col):

    """
    Splits combined classifications into separate tables and tidies them.
    """

    return (df[df["classification_type"] == classification_type]
        .drop_duplicates(subset=["classification_desc"], keep="first")
        .drop(columns=["registered_num", "classification_type"])
        .rename(columns={"classification_code": id_col, "classification_desc": name_col})
    )

def transform_join_tables(df, classification_type, id_col):

    """
    Builds join tables to manage many-to-many relationships between funders and their classifications.
    """

    result = df[df["classification_type"] == classification_type
        ].drop(columns=["classification_type", "classification_desc"]
        ).rename(columns={"classification_code": id_col})

    result = result[result["registered_num"].notna() & (result["registered_num"] != "")]

    return result

def ensure_area_columns(df_exploded, col_name, expected_cols):

    """
    Ensures columns are present and normalised.
    """

    normalised_df = pd.json_normalize(df_exploded[col_name])

    for col in expected_cols:
        if col not in normalised_df.columns:
            normalised_df[col] = None

    normalised_df = normalised_df.reindex(columns=expected_cols)
    normalised_df.columns = ["area_" + col for col in normalised_df.columns]

    return normalised_df

def transform_financials_df(financial_data):

    """
    Converts raw financial history data list into a dataframe.
    """

    df = pd.DataFrame(financial_data)

    #extract year from date string
    df["year"] = df["financial_period_end_date"].apply(
        lambda x: int(x.split("-")[0]) if x else None
    )

    return df

def transform_financials_long(df):

    """
    Transforms financial data from wide to long format (one row per financial record type).
    """

    financials_rows = []

    for _, row in df.iterrows():
        reg_num = row["reg_charity_number"]
        year = row["year"]

        if pd.isna(year):
            continue

        #create income record if exists
        if pd.notna(row["income"]):
            financials_rows.append({
                "financials_id": f"{reg_num}_{year}_income",
                "financials_year": year,
                "financials_type": "income",
                "financials_value": row["income"]
            })

        #create expenditure record if exists
        if pd.notna(row["expenditure"]):
            financials_rows.append({
                "financials_id": f"{reg_num}_{year}_expenditure",
                "financials_year": year,
                "financials_type": "expenditure",
                "financials_value": row["expenditure"]
            })

    return pd.DataFrame(financials_rows)

def transform_financials_join(df):

    """
    Creates join table linking funders to their financial records.
    """

    join_rows = []

    for _, row in df.iterrows():
        reg_num = str(row["reg_charity_number"])
        year = row["year"]

        if pd.isna(year):
            continue

        #create join record for income if exists
        if pd.notna(row["income"]):
            join_rows.append({
                "registered_num": reg_num,
                "financials_id": f"{reg_num}_{year}_income"
            })

        #create join record for expenditure if exists
        if pd.notna(row["expenditure"]):
            join_rows.append({
                "registered_num": reg_num,
                "financials_id": f"{reg_num}_{year}_expenditure"
            })

    return pd.DataFrame(join_rows)
