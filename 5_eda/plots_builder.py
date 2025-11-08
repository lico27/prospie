import matplotlib.pyplot as plt
from utils import explode_lists

def make_bar_chart(df, col, title, color="#2E86AB"):
    """
    Creates a bar chart to display most popular categories.
    """
    counts = explode_lists(df, col)[col].value_counts().head(10)
    total = explode_lists(df, col)[col].count()
    percentages = (counts / total * 100)

    _, ax = plt.subplots(figsize=(10, 6))
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

    plt.tight_layout()
    plt.show()