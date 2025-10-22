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
