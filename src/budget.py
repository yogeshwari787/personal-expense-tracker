"""
budget.py - Monthly Budget Management & Overspending Detection
Enables setting category-specific spending caps and monitors budget utilization.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, Optional
import os
from database import get_connection, DEFAULT_DB_PATH


def set_budget(
    month: str,
    category_name: str,
    limit_amount: float,
    db_path: str = DEFAULT_DB_PATH
) -> None:
    """Inserts or updates a monthly budget for a specific category."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO budgets (month, category_name, limit_amount)
        VALUES (?, ?, ?)
        ON CONFLICT(month, category_name) 
        DO UPDATE SET limit_amount = excluded.limit_amount;
    """, (month, category_name, float(limit_amount)))
    conn.commit()
    conn.close()


def seed_default_budgets(month: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """Seeds reasonable default monthly budget caps for standard categories."""
    default_limits = {
        "Rent & Housing": 12500.0,
        "Groceries": 5000.0,
        "Food & Dining": 3000.0,
        "Transportation": 2000.0,
        "Utilities": 2500.0,
        "Shopping": 4000.0,
        "Entertainment": 1500.0,
        "Health & Fitness": 2000.0,
        "Subscriptions": 1000.0,
        "Miscellaneous": 1500.0
    }
    for cat, limit in default_limits.items():
        set_budget(month, cat, limit, db_path=db_path)


def check_budget_status(
    df: pd.DataFrame,
    month: str,
    db_path: str = DEFAULT_DB_PATH
) -> pd.DataFrame:
    """
    Compares actual spending against defined budgets for a given month ('YYYY-MM').
    Returns DataFrame with columns:
    ['Category', 'Budget_Limit', 'Actual_Spend', 'Variance', 'Pct_Utilized', 'Status']
    """
    conn = get_connection(db_path)
    budgets_df = pd.read_sql_query(
        "SELECT category_name AS Category, limit_amount AS Budget_Limit FROM budgets WHERE month = ?",
        conn,
        params=[month]
    )
    conn.close()

    # Filter expenses for the specific month
    df_copy = df.copy()
    df_copy["Month"] = df_copy["Date"].astype(str).str.slice(0, 7)
    
    # Exclude income transactions from expense budget tracking
    expenses = df_copy[(df_copy["Month"] == month) & (df_copy["Category"].str.lower() != "income")]
    actual_spend = expenses.groupby("Category")["Amount"].sum().reset_index()
    actual_spend = actual_spend.rename(columns={"Amount": "Actual_Spend"})

    if budgets_df.empty:
        # If no budget set, generate based on default categories
        seed_default_budgets(month, db_path=db_path)
        conn = get_connection(db_path)
        budgets_df = pd.read_sql_query(
            "SELECT category_name AS Category, limit_amount AS Budget_Limit FROM budgets WHERE month = ?",
            conn,
            params=[month]
        )
        conn.close()

    merged = pd.merge(budgets_df, actual_spend, on="Category", how="outer").fillna(0.0)
    merged["Variance"] = (merged["Budget_Limit"] - merged["Actual_Spend"]).round(2)
    merged["Pct_Utilized"] = (merged["Actual_Spend"] / merged["Budget_Limit"].replace(0, 1) * 100).round(1)

    def determine_status(row):
        if row["Budget_Limit"] == 0:
            return "No Budget Set"
        elif row["Actual_Spend"] > row["Budget_Limit"]:
            return "EXCEEDED"
        elif row["Pct_Utilized"] >= 85:
            return "WARNING"
        return "WITHIN LIMIT"

    merged["Status"] = merged.apply(determine_status, axis=1)
    merged = merged.sort_values(by="Actual_Spend", ascending=False).reset_index(drop=True)
    return merged
