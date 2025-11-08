import pandas as pd

def add_gbp_columns(x):
    """
    Adds a new column with currency formatted in GBP.
    """
    return f"£{x:,.2f}" if pd.notnull(x) else ""

def explode_lists(df, col):
    """
    Explodes a list column to create one row per list item.
    """
    return df.explode(col).dropna(subset=[col])
