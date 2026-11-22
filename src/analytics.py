"""
analytics.py - Financial Aggregations & Key Performance Indicators (KPIs)
Calculates summary statistics, category breakdown, monthly trends, payment methods,
and spending velocity metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes primary personal finance health indicators.
    Separates Income vs Expenses.
    """
    df_clean = df.copy()

    # Separate Income and Expenses
    income_mask = df_clean["Category"].str.lower() == "income"
    expense_df = df_clean[~income_mask]
    income_df = df_clean[income_mask]

    total_spend = round(float(expense_df["Amount"].sum()), 2)
    total_income = round(float(income_df["Amount"].sum()), 2)
    net_savings = round(total_income - total_spend, 2)
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    # Date range calculations
    if not expense_df.empty:
        min_str = str(expense_df["Date"].min())[:10]
        max_str = str(expense_df["Date"].max())[:10]
        try:
            min_dt = datetime.strptime(min_str, "%Y-%m-%d")
            max_dt = datetime.strptime(max_str, "%Y-%m-%d")
            total_days = max(1, (max_dt - min_dt).days + 1)
        except Exception:
            total_days = 30
        avg_daily_spend = round(total_spend / total_days, 2)
    else:
        avg_daily_spend = 0.0

    # Highest spending category
    if not expense_df.empty:
        cat_sums = expense_df.groupby("Category")["Amount"].sum()
        highest_cat = cat_sums.idxmax()
        highest_cat_amt = round(float(cat_sums.max()), 2)
        highest_cat_pct = round((highest_cat_amt / total_spend * 100), 1) if total_spend > 0 else 0.0
    else:
        highest_cat = "None"
        highest_cat_amt = 0.0
        highest_cat_pct = 0.0

    return {
        "total_spend": total_spend,
        "total_income": total_income,
        "net_savings": net_savings,
        "savings_rate_pct": savings_rate,
        "avg_daily_spend": avg_daily_spend,
        "highest_spending_category": highest_cat,
        "highest_category_amount": highest_cat_amt,
        "highest_category_pct": highest_cat_pct,
        "total_transactions": len(df_clean),
        "expense_transactions": len(expense_df),
        "income_transactions": len(income_df)
    }


def get_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Computes total spend and percentage share per expense category."""
    expense_df = df[df["Category"].str.lower() != "income"].copy()
    if expense_df.empty:
        return pd.DataFrame(columns=["Category", "Amount", "Percentage", "Tx_Count"])

    total = expense_df["Amount"].sum()
    summary = (
        expense_df.groupby("Category")
        .agg(Amount=("Amount", "sum"), Tx_Count=("Amount", "count"))
        .reset_index()
    )
    summary["Percentage"] = (summary["Amount"] / total * 100).round(2)
    summary = summary.sort_values(by="Amount", ascending=False).reset_index(drop=True)
    summary["Amount"] = summary["Amount"].round(2)
    return summary


def get_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Computes month-over-month Income, Expense, Net Savings, and Savings Rate."""
    df_clean = df.copy()
    df_clean["Month"] = df_clean["Date"].astype(str).str.slice(0, 7)

    # Pivot income and expenses by month
    grouped = []
    for month, group in df_clean.groupby("Month"):
        income = group[group["Category"].str.lower() == "income"]["Amount"].sum()
        expense = group[group["Category"].str.lower() != "income"]["Amount"].sum()
        savings = income - expense
        rate = round((savings / income * 100), 1) if income > 0 else 0.0
        grouped.append({
            "Month": str(month),
            "Income": round(income, 2),
            "Expense": round(expense, 2),
            "Savings": round(savings, 2),
            "Savings_Rate_Pct": rate,
            "Tx_Count": len(group)
        })

    return pd.DataFrame(grouped).sort_values("Month").reset_index(drop=True)


def get_payment_method_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Computes spending distribution grouped by payment method."""
    expense_df = df[df["Category"].str.lower() != "income"].copy()
    if expense_df.empty:
        return pd.DataFrame(columns=["Payment_Method", "Amount", "Percentage", "Tx_Count"])

    total = expense_df["Amount"].sum()
    summary = (
        expense_df.groupby("Payment_Method")
        .agg(Amount=("Amount", "sum"), Tx_Count=("Amount", "count"))
        .reset_index()
    )
    summary["Percentage"] = (summary["Amount"] / total * 100).round(2)
    summary = summary.sort_values(by="Amount", ascending=False).reset_index(drop=True)
    summary["Amount"] = summary["Amount"].round(2)
    return summary


def get_daily_spending_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates daily expense sums with a 7-day moving average."""
    expense_df = df[df["Category"].str.lower() != "income"].copy()
    if expense_df.empty:
        return pd.DataFrame(columns=["Date", "Amount", "Rolling_7D_Avg"])

    daily = expense_df.groupby("Date")["Amount"].sum().reset_index()
    daily = daily.sort_values("Date").reset_index(drop=True)
    daily["Rolling_7D_Avg"] = daily["Amount"].rolling(window=7, min_periods=1).mean().round(2)
    daily["Date"] = daily["Date"].astype(str).str.slice(0, 10)
    return daily


def get_top_expenses(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Returns top N single highest expense transactions."""
    expense_df = df[df["Category"].str.lower() != "income"].copy()
    return (
        expense_df.sort_values(by="Amount", ascending=False)
        .head(n)[["Date", "Category", "Amount", "Payment_Method", "Description"]]
        .reset_index(drop=True)
    )
