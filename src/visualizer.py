"""
visualizer.py - Publication-Quality Charts with Matplotlib & Seaborn
Generates clean, aesthetic financial visualizations and exports high-DPI images.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Headless backend safe for servers and CLI
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional


# Set professional aesthetic theme
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "figure.titlesize": 15
})


def plot_category_distribution(
    df: pd.DataFrame,
    output_path: str = "images/category_distribution.png"
) -> str:
    """Generates a horizontal bar chart displaying category-wise spending."""
    from analytics import get_category_summary

    cat_df = get_category_summary(df)
    if cat_df.empty:
        return ""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = sns.color_palette("mako", len(cat_df))
    bars = ax.barh(cat_df["Category"][::-1], cat_df["Amount"][::-1], color=colors, edgecolor="black", alpha=0.85)

    # Add data labels
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + (max(cat_df["Amount"]) * 0.01),
            bar.get_y() + bar.get_height() / 2,
            f" ₹{width:,.0f}",
            va="center",
            ha="left",
            fontsize=9,
            fontweight="semibold"
        )

    ax.set_title("Category-Wise Expense Breakdown", pad=15)
    ax.set_xlabel("Total Spend (INR ₹)")
    ax.set_ylabel("Expense Category")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_monthly_trend(
    df: pd.DataFrame,
    output_path: str = "images/monthly_trend.png"
) -> str:
    """Generates a dual comparison of Monthly Income vs Expense trends."""
    from analytics import get_monthly_summary

    monthly_df = get_monthly_summary(df)
    if monthly_df.empty:
        return ""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(
        monthly_df["Month"],
        monthly_df["Expense"],
        marker="o",
        linewidth=2.5,
        color="#e74c3c",
        label="Monthly Expenses"
    )
    ax.fill_between(monthly_df["Month"], monthly_df["Expense"], color="#e74c3c", alpha=0.15)

    if monthly_df["Income"].sum() > 0:
        ax.plot(
            monthly_df["Month"],
            monthly_df["Income"],
            marker="s",
            linewidth=2.5,
            color="#2ecc71",
            linestyle="--",
            label="Monthly Income"
        )

    for i, txt in enumerate(monthly_df["Expense"]):
        ax.annotate(
            f"₹{txt:,.0f}",
            (monthly_df["Month"].iloc[i], monthly_df["Expense"].iloc[i]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontweight="bold",
            fontsize=9
        )

    ax.set_title("Monthly Spending & Income Trend", pad=15)
    ax.set_xlabel("Billing Month")
    ax.set_ylabel("Amount (INR ₹)")
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_payment_methods(
    df: pd.DataFrame,
    output_path: str = "images/payment_methods.png"
) -> str:
    """Generates an aesthetic donut chart showing payment method distribution."""
    from analytics import get_payment_method_summary

    pm_df = get_payment_method_summary(df)
    if pm_df.empty:
        return ""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 7))

    colors = sns.color_palette("Blues_r", len(pm_df))
    wedges, texts, autotexts = ax.pie(
        pm_df["Amount"],
        labels=pm_df["Payment_Method"],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )

    for at in autotexts:
        at.set_color("black")
        at.set_fontsize(9)
        at.set_fontweight("bold")

    ax.set_title("Payment Method Share", pad=15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_daily_spending(
    df: pd.DataFrame,
    output_path: str = "images/daily_spending.png"
) -> str:
    """Generates a timeline of daily spending with 7-day rolling average."""
    from analytics import get_daily_spending_trend

    daily_df = get_daily_spending_trend(df)
    if daily_df.empty:
        return ""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5))

    ax.bar(daily_df["Date"], daily_df["Amount"], color="#3498db", alpha=0.4, label="Daily Spending")
    ax.plot(daily_df["Date"], daily_df["Rolling_7D_Avg"], color="#e67e22", linewidth=2.5, label="7-Day Moving Avg")

    # Limit x-ticks to avoid congestion
    ticks_to_show = daily_df["Date"].iloc[::max(1, len(daily_df) // 8)]
    ax.set_xticks(ticks_to_show)
    ax.set_xticklabels(ticks_to_show, rotation=35, ha="right")

    ax.set_title("Daily Spending Velocity & 7-Day Moving Average", pad=15)
    ax.set_xlabel("Transaction Date")
    ax.set_ylabel("Spend (INR ₹)")
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def generate_all_plots(df: pd.DataFrame, output_dir: str = "images") -> dict:
    """Generates and saves all primary financial charts."""
    return {
        "category_chart": plot_category_distribution(df, os.path.join(output_dir, "category_distribution.png")),
        "monthly_chart": plot_monthly_trend(df, os.path.join(output_dir, "monthly_trend.png")),
        "payment_chart": plot_payment_methods(df, os.path.join(output_dir, "payment_methods.png")),
        "daily_chart": plot_daily_spending(df, os.path.join(output_dir, "daily_spending.png"))
    }
