"""
reporter.py - Monthly Financial Report & Insight Generator
Generates structured CSV summaries and comprehensive plain-text/markdown audit reports.
"""

import os
import pandas as pd
from typing import Dict, Any
from datetime import datetime


def generate_csv_report(
    df: pd.DataFrame,
    output_path: str = "reports/monthly_summary_report.csv"
) -> str:
    """Exports category-wise and month-wise spending aggregations to CSV."""
    from analytics import get_category_summary, get_monthly_summary

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cat_df = get_category_summary(df)
    cat_df.to_csv(output_path, index=False)
    return output_path


def generate_text_report(
    kpis: Dict[str, Any],
    cat_summary: pd.DataFrame,
    monthly_summary: pd.DataFrame,
    budget_summary: pd.DataFrame,
    output_path: str = "reports/financial_insights.txt"
) -> str:
    """
    Generates an executive-level personal financial audit report
    with metrics, spending health score, budget breaches, and savings advice.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Calculate financial health score (0 to 100)
    savings_rate = kpis["savings_rate_pct"]
    if savings_rate >= 30:
        health_score = 90
        health_badge = "EXCELLENT (Strong Savings Discipline)"
    elif savings_rate >= 20:
        health_score = 75
        health_badge = "HEALTHY (Meets Recommended 50-30-20 Rule)"
    elif savings_rate >= 10:
        health_score = 60
        health_badge = "MODERATE (Room for Expense Optimization)"
    else:
        health_score = 40
        health_badge = "VULNERABLE (High Spending Ratio)"

    lines = []
    lines.append("=" * 72)
    lines.append("       PERSONAL EXPENSE TRACKER - MONTHLY FINANCIAL AUDIT REPORT")
    lines.append("=" * 72)
    lines.append(f"Generated On          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Financial Health Score: {health_score}/100 -> {health_badge}")
    lines.append("-" * 72)
    lines.append("1. EXECUTIVE FINANCIAL SUMMARY")
    lines.append("-" * 72)
    lines.append(f"  • Total Income Recorded   : ₹{kpis['total_income']:,.2f}")
    lines.append(f"  • Total Expenses Incurred : ₹{kpis['total_spend']:,.2f}")
    lines.append(f"  • Net Savings             : ₹{kpis['net_savings']:,.2f}")
    lines.append(f"  • Overall Savings Rate    : {kpis['savings_rate_pct']:.1f}%")
    lines.append(f"  • Average Daily Spend     : ₹{kpis['avg_daily_spend']:,.2f}")
    lines.append(f"  • Highest Spend Category  : {kpis['highest_spending_category']} (₹{kpis['highest_category_amount']:,.2f} | {kpis['highest_category_pct']:.1f}% of total)")
    lines.append(f"  • Total Transactions      : {kpis['total_transactions']} ({kpis['expense_transactions']} debits, {kpis['income_transactions']} credits)")
    lines.append("")
    lines.append("-" * 72)
    lines.append("2. CATEGORY-WISE SPENDING BREAKDOWN")
    lines.append("-" * 72)
    lines.append(f"{'Category':<22} | {'Amount (INR)':<14} | {'% Share':<9} | {'Tx Count'}")
    lines.append("-" * 72)
    for _, row in cat_summary.iterrows():
        lines.append(f"{row['Category']:<22} | ₹{row['Amount']:<13,.2f} | {row['Percentage']:<8.1f}% | {row['Tx_Count']}")
    lines.append("")
    lines.append("-" * 72)
    lines.append("3. MONTH-OVER-MONTH CASH FLOW")
    lines.append("-" * 72)
    lines.append(f"{'Month':<10} | {'Income (INR)':<14} | {'Expense (INR)':<14} | {'Savings (INR)':<14} | {'Savings %'}")
    lines.append("-" * 72)
    for _, row in monthly_summary.iterrows():
        lines.append(f"{row['Month']:<10} | ₹{row['Income']:<13,.2f} | ₹{row['Expense']:<13,.2f} | ₹{row['Savings']:<13,.2f} | {row['Savings_Rate_Pct']:.1f}%")
    lines.append("")
    lines.append("-" * 72)
    lines.append("4. BUDGET VARIANCE & OVERSPEND MONITOR")
    lines.append("-" * 72)
    lines.append(f"{'Category':<20} | {'Budget':<11} | {'Actual':<11} | {'Variance':<11} | {'Status'}")
    lines.append("-" * 72)
    for _, row in budget_summary.iterrows():
        status_str = f"[{row['Status']}]"
        lines.append(f"{row['Category']:<20} | ₹{row['Budget_Limit']:<10,.0f} | ₹{row['Actual_Spend']:<10,.0f} | ₹{row['Variance']:<10,.0f} | {status_str}")
    lines.append("")
    lines.append("-" * 72)
    lines.append("5. ACTIONABLE PERSONAL FINANCE RECOMMENDATIONS")
    lines.append("-" * 72)

    # Generate custom tips based on actual findings
    if kpis["highest_spending_category"] in ["Food & Dining", "Shopping"]:
        lines.append("  [!] Discretionary Warning: Major spend concentrated in non-essential category.")
        lines.append(f"      Recommendation: Cap {kpis['highest_spending_category']} with weekly budget limits to save up to 15%.")

    exceeded = budget_summary[budget_summary["Status"] == "EXCEEDED"]
    if not exceeded.empty:
        cats = ", ".join(exceeded["Category"].tolist())
        lines.append(f"  [!] Budget Breaches Detected in: {cats}.")
        lines.append("      Recommendation: Audit recent transactions in these areas and enable real-time spend alerts.")
    else:
        lines.append("  [✓] All monitored categories remained within planned budgetary limits.")

    lines.append("  [✓] Follow the 50/30/20 Rule: 50% Needs (Rent, Bills), 30% Wants (Dining, Shopping), 20% Savings.")
    lines.append("=" * 72)

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path
