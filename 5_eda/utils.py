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

def make_summary_df(funders_df, grants_df):
    summary_data = {
        "Metric": [
            "Total funders",
            "Total recipients",
            "Total grants",
            "Total grant value",
            "Mean grants per funder",
            "Most grants given by a funder",
            "Fewest grants given by a funder",
            "Mean recipients per funder",
            "Mean areas per funder",
            "Mean funder income",
            "Median funder income",
            "Mean funder expenditure",
            "Median funder expenditure",
            "Largest funder by income",
            "Largest funder by expenditure",
            "Mean grants per recipient",
            "Range of grants received",
            "Recipient of largest grant",
            "Mean grant size",
            "Median grant size",
            "Standard deviation",
            "Smallest grant",
            "Largest grant",
            
        ],
        "Value": [
            len(funders_df["registered_num"].unique()),
            len(grants_df["recipient_id"].unique()),
            len(grants_df["grant_id"].unique()),
            grants_df["amount"].sum(),
            funders_df["num_grants"].mean(),
            funders_df["num_grants"].max(),
            funders_df["num_grants"].min(),
            grants_df.groupby("funder_num")["recipient_id"].nunique().mean(),
            funders_df["areas"].apply(len).mean(),
            funders_df["income"].mean(),
            funders_df["income"].median(),
            funders_df["expenditure"].mean(),
            funders_df["expenditure"].median(),
            f"{funders_df.loc[funders_df.loc[funders_df['income'] > 0, 'income'].idxmax(), 'name']} (£{funders_df.loc[funders_df.loc[funders_df['income'] > 0, 'income'].idxmax(), 'income']:,.2f})",
            f"{funders_df.loc[funders_df.loc[funders_df['expenditure'] > 0, 'expenditure'].idxmax(), 'name']} (£{funders_df.loc[funders_df.loc[funders_df['expenditure'] > 0, 'expenditure'].idxmax(), 'expenditure']:,.2f})",
            grants_df.groupby("recipient_id")["grant_id"].nunique().mean(),
            f"{grants_df.groupby('recipient_id')['grant_id'].nunique().min():.0f} to {grants_df.groupby('recipient_id')['grant_id'].nunique().max():.0f}",
            f"{grants_df.loc[grants_df.loc[grants_df['amount'] > 0, 'amount'].idxmax(), 'recipient_name']} (£{grants_df.loc[grants_df.loc[grants_df['amount'] > 0, 'amount'].idxmax(), 'amount']:,.2f}) from {grants_df.loc[grants_df.loc[grants_df['amount'] > 0, 'amount'].idxmax(), 'funder_name']}",
            grants_df["amount"].mean(),
            grants_df["amount"].median(),
            grants_df["amount"].std(),
            grants_df.loc[grants_df["amount"] > 0, "amount"].min(),
            grants_df["amount"].max()
        ]
    }
    return summary_data

def format_stats(row):
    if row["Metric"] == "Range of grants received":
        return row["Value"]
    elif row["Metric"] in ["Mean recipients per funder", "Mean areas per funder", "Mean grants per recipient"]:
        return f"{row['Value']:,.1f}"
    elif row["Metric"] in ["Total grant value", "Mean grant size", "Median grant size", "Smallest grant", "Largest grant", "Median funder income", "Median funder expenditure", "Mean funder income", "Mean funder expenditure", "Standard deviation"]:
        return f"£{row['Value']:,.2f}"
    elif row["Metric"] in ["Largest funder by income", "Largest funder by expenditure", "Recipient of largest grant"]:
        return row['Value'].title()
    else:
        return f"{row['Value']:,.0f}"