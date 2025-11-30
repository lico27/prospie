import pandas as pd
import re
from names_dataset import NameDataset
nd = NameDataset()

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

def get_longest_values(df, col, id_col, n=10):
    """
    Gets a list of the IDs for the top n longest values in a column.
    """
    df_no_nas = df.dropna(subset=[col])
    longest = df_no_nas.sort_values(col, ascending=False).head(n)[id_col].tolist()
    return longest

def print_in_rows(items, num_per_row):
    items_list = list(items)
    for i in range(0, len(items_list), num_per_row):
        print(", ".join(items_list[i:i+num_per_row]))

def check_names(name):
    """
    Checks if a value in recipient_name is likely to be the name of an individual person, not an organisation.
    """
    if pd.isna(name) or not isinstance(name, str):
        return False
    
    name = name.strip()

    #check for title
    if name.upper().startswith("MR ") or name.upper().startswith("MRS ") or name.upper().startswith("MISS "):
        return True

    words = name.split()
    
    #filter to two words (to capture firstname lastname)
    if len(words) != 2:
        return False
    
    first, last = words
    
    #filter out numbers
    if any(char.isdigit() for char in name):
        return False
    
    #search names dataset
    first_check = nd.search(first)
    last_check = nd.search(last)
    
    #filter out nonexistent names
    if first_check.get("first_name") is None and first_check.get("last_name") is None:
        return False
    if last_check.get("first_name") is None and last_check.get("last_name") is None:
        return False
    
    return True

def check_overlap(list1, list2):
    """
    Checks if two lists overlap.
    """
    if not list1 or not list2:
        return False
    return len(set(list1) & set(list2)) > 0

def clean_start_of_text(text):
    """
    Removes non-alphanumeric characters from the start of text columns.
    """
    if not isinstance(text, str) or not text:
        return text

    cleaned = re.sub(r'^[^a-zA-Z0-9]+', '', text)
    
    return cleaned if cleaned else None