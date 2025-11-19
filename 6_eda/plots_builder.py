import matplotlib.pyplot as plt
from eda_utils import explode_lists

def make_bar_chart(df, col, title, color="#2E86AB", ax=None):
    """
    Creates a bar chart to display most popular categories.
    Can accept an optional ax parameter to plot on an existing axis.
    """
    counts = explode_lists(df, col)[col].value_counts().head(10)
    total = explode_lists(df, col)[col].count()
    percentages = (counts / total * 100)

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 6))
        show_plot = True
    else:
        show_plot = False

    bars = ax.barh(range(len(counts)), counts.values, color=color, alpha=0.8)

    #edit formatting and labels
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index)
    ax.set_xlabel("Number of Funders", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=20)
    ax.invert_yaxis()

    #include proportions as labels
    for i, (_, value, pct) in enumerate(zip(bars, counts.values, percentages)):
        ax.text(value + max(counts.values)*0.01, i, f'{int(value)} ({pct:.1f}%)',
                va="center", fontsize=9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    if show_plot:
        plt.tight_layout()
        plt.show()
    
def make_histograms(match_rates_df):
    """
    Makes histograms comparing causes, areas, and beneficiaries match rates.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for idx, (category, color) in enumerate([("causes", "#2E86AB"),
                                            ("areas", "#A23B72"),
                                            ("beneficiaries", "#F18F01")]):
        col = f"{category}_match_rate"
        mean_val = match_rates_df[col].mean()

        axes[idx].hist(match_rates_df[col], bins=20, color=color, edgecolor="black")
        axes[idx].axvline(mean_val, color="red", linestyle="--", linewidth=2,
                        label=f"Mean: {mean_val:.1%}")
        axes[idx].set_xlabel("Match Rate")
        axes[idx].set_ylabel("Number of Funders")
        axes[idx].set_title(f"{category.title()} Match Rate Distribution")
        axes[idx].legend()

    plt.tight_layout()
    plt.show()