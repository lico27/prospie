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

def check_word_counts(df, col, n=10):
    """
    Gets longest and shortest registered_nums for a word count column.
    """
    df_no_nas = df.dropna(subset=[col])
    longest = df_no_nas.sort_values(col, ascending=False).head(n)["registered_num"].tolist()
    shortest = df_no_nas.sort_values(col, ascending=True).head(n)["registered_num"].tolist()
    return longest, shortest

def print_in_rows(items, num_per_row):
    items_list = list(items)
    for i in range(0, len(items_list), num_per_row):
        print(", ".join(items_list[i:i+num_per_row]))