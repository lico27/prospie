import pandas as pd
from IPython.display import display
import numpy as np

def get_historical_mean(financials_dict):
    """
    Calculates mean for historical financials data
    """
    if not financials_dict or not isinstance(financials_dict, dict):
        return np.nan
    values = [v for v in financials_dict.values() if pd.notna(v) and v > 0]
    return np.mean(values) if values else np.nan

def get_historical_median(financials_dict):
    """
    Calculates median for historical financials data.
    """
    if not financials_dict or not isinstance(financials_dict, dict):
        return np.nan
    values = [v for v in financials_dict.values() if pd.notna(v) and v > 0]
    return np.median(values) if values else np.nan

def make_summary_df(funders_df, grants_df):
    """
    Creates a dictionary of summary statistics for funders and grants.
    """
    #get averages for historical financials data
    funders_df_calc = funders_df.copy()
    funders_df_calc["income_hist_mean"] = funders_df_calc["income_history"].apply(get_historical_mean)
    funders_df_calc["income_hist_median"] = funders_df_calc["income_history"].apply(get_historical_median)
    funders_df_calc["expenditure_hist_mean"] = funders_df_calc["expenditure_history"].apply(get_historical_mean)
    funders_df_calc["expenditure_hist_median"] = funders_df_calc["expenditure_history"].apply(get_historical_median)

    #prefer mean but use latest if not available
    funders_df_calc["income_for_stats"] = funders_df_calc["income_hist_mean"].combine_first(funders_df_calc["income_latest"])
    funders_df_calc["expenditure_for_stats"] = funders_df_calc["expenditure_hist_mean"].combine_first(funders_df_calc["expenditure_latest"])

    #calculate stats
    mean_income = funders_df_calc["income_for_stats"].mean()
    median_income = funders_df_calc["income_hist_median"].combine_first(funders_df_calc["income_latest"]).median()
    mean_expenditure = funders_df_calc["expenditure_for_stats"].mean()
    median_expenditure = funders_df_calc["expenditure_hist_median"].combine_first(funders_df_calc["expenditure_latest"]).median()
    largest_by_income_idx = funders_df_calc.loc[funders_df_calc["income_for_stats"] > 0, "income_for_stats"].idxmax()
    largest_by_expenditure_idx = funders_df_calc.loc[funders_df_calc["expenditure_for_stats"] > 0, "expenditure_for_stats"].idxmax()

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
            "Largest funder by mean income",
            "Largest funder by mean expenditure",
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
            mean_income,
            median_income,
            mean_expenditure,
            median_expenditure,
            f"{funders_df_calc.loc[largest_by_income_idx, 'name']} (£{funders_df_calc.loc[largest_by_income_idx, 'income_for_stats']:,.2f})",
            f"{funders_df_calc.loc[largest_by_expenditure_idx, 'name']} (£{funders_df_calc.loc[largest_by_expenditure_idx, 'expenditure_for_stats']:,.2f})",
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

def calculate_stats(funders_df, grants_df):
    """
    Calculates some additional statistics for funders and grants.
    """
    #find share of 90th percentile funders
    percentile_90_funders = funders_df[funders_df["num_grants"] >= funders_df["num_grants"].quantile(0.9)]
    top_funders_share = (percentile_90_funders["num_grants"].sum() / funders_df["num_grants"].sum()) * 100

    #find share of 90th percentile recipients
    recipient_totals = grants_df.groupby("recipient_id")["amount"].sum()
    percentile_90_recipients = recipient_totals[recipient_totals >= recipient_totals.quantile(0.9)].sum()
    top_recipients_share = (percentile_90_recipients / grants_df["amount"].sum()) * 100

    #find repeat grant funder-recipient pairs
    funder_recipient_pairs = grants_df.groupby(["funder_num", "recipient_id"])["grant_id"].count()
    repeat_grants = (funder_recipient_pairs > 1).sum()
    total_pairs = len(funder_recipient_pairs)
    repeat_grants_pct = (repeat_grants / total_pairs) * 100
    avg_grants_per_pair = funder_recipient_pairs.mean()

    #find historical averages and ratios
    grants_last_year = grants_df[grants_df["year"] == grants_df["year"].max()].groupby("funder_num")["amount"].sum()
    funders_calc = funders_df.set_index("registered_num").copy()
    funders_calc["income_hist_mean"] = funders_calc["income_history"].apply(get_historical_mean)
    funders_calc["income_for_ratio"] = funders_calc["income_hist_mean"].combine_first(funders_calc["income_latest"])

    giving_ratios = funders_calc[["income_for_ratio"]].copy()
    giving_ratios["grants_last_year"] = grants_last_year
    giving_ratios["grants_to_income_ratio"] = (giving_ratios["grants_last_year"] / giving_ratios["income_for_ratio"]) * 100
    get_ratios = giving_ratios.loc[(giving_ratios["income_for_ratio"] > 0) & (giving_ratios["grants_to_income_ratio"].notna()),"grants_to_income_ratio"]
    mean_grants_to_income = get_ratios.mean()
    median_grants_to_income = get_ratios.median()

    #find share of funders supporting general charitable purposes only
    gcp_funders = funders_df[(funders_df["causes"].apply(len) == 1) & (funders_df["causes"].apply(lambda x: "101" in x))]
    gcp_pct = (len(gcp_funders) / len(funders_df)) * 100

    return top_funders_share, top_recipients_share, repeat_grants_pct, avg_grants_per_pair, mean_grants_to_income, median_grants_to_income, gcp_pct

def make_calculated_df(stats):
    """
    Creates a dictionary of calculated statistics.
    """
    calculated_data = {
        "Metric":
        ["Share of grants from top 10% funders (by income)",
        "Share of grants to top 10% recipients (by grant value)",
        "Percent of recipients with multiple grants from same funder",
        "Average grants per funder-recipient pair",
        "Mean grants-to-income ratio",
        "Median grants-to-income ratio",
        "Percent of funders supporting General Charitable Purposes only",
        ],
        "Value": stats
    }
    return calculated_data

def format_stats(row):
    """
    Formats statistics values based on their metric type.
    """
    if row["Metric"] == "Range of grants received":
        return row["Value"]
    elif row["Metric"] in ["Mean recipients per funder",
                           "Mean areas per funder",
                           "Mean grants per recipient"]:
        return f"{row['Value']:,.1f}"
    elif row["Metric"] in ["Total grant value",
                           "Mean grant size",
                           "Median grant size",
                           "Smallest grant",
                           "Largest grant",
                           "Median funder income",
                           "Median funder expenditure",
                           "Mean funder income",
                           "Mean funder expenditure",
                           "Median funder income",
                           "Median funder expenditure",
                           "Mean funder income",
                           "Mean funder expenditure",
                           "Standard deviation"]:
        return f"£{row['Value']:,.2f}"
    elif row["Metric"] in ["Largest funder by mean income",
                           "Largest funder by mean expenditure",
                           "Recipient of largest grant"]:
        return row['Value'].title()
    elif row["Metric"] in ["Share of grants from top 10% funders (by income)",
                           "Share of grants to top 10% recipients (by grant value)",
                           "Percent of recipients with multiple grants from same funder",
                           "Percent of funders supporting General Charitable Purposes only",
                           "Mean grants-to-income ratio",
                           "Median grants-to-income ratio"]:
        return f"{row['Value']:,.1f}%"
    else:
        if isinstance(row['Value'], str):
            return row['Value']
        return f"{row['Value']:,.0f}"
    
def format_df(df):
    """
    Formats a dataframe for display.
    """
    display(df.style
    .set_properties(**{"text-align": "left"})
    .set_table_styles([
        {"selector": "th", "props": [("font-weight", "bold"), ("text-align", "left"), ("border-bottom", "1px solid")]},
        {"selector": "td", "props": [("padding", "6px")]}
    ])
    .hide(axis="index")
)
