"""
main.py - Personal Expense Tracker with Data Visualization (Execution Driver)
Runs the entire end-to-end pipeline:
1. Ingestion / Data Loading
2. Data Preprocessing & Sanitization
3. Smart Categorization
4. SQLite Database Persistence
5. Financial KPIs & Analytics
6. Chart Visualization Generation (Matplotlib & Seaborn)
7. Audit Report & CSV Export
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

# Configure writable matplotlib cache directory
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib_cache")
os.makedirs("/tmp/matplotlib_cache", exist_ok=True)

import argparse
import pandas as pd

# Add src directory to system path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)

from database import init_db, insert_transaction, fetch_all_transactions, DEFAULT_DB_PATH
from data_loader import load_expense_csv, generate_synthetic_expenses
from data_cleaner import clean_expense_data
from categorizer import auto_categorize
from analytics import (
    calculate_kpis,
    get_category_summary,
    get_monthly_summary,
    get_payment_method_summary,
    get_daily_spending_trend,
    get_top_expenses
)
from visualizer import generate_all_plots
from reporter import generate_csv_report, generate_text_report
from budget import check_budget_status, seed_default_budgets


def print_banner():
    banner = """
========================================================================
    💸 PERSONAL EXPENSE TRACKER WITH DATA VISUALIZATION 💸
      Automated Pipeline: Ingest -> Clean -> Analyze -> Visualize
========================================================================
"""
    print(banner)


def run_pipeline(csv_path: str = None, generate_synthetic: bool = False, num_samples: int = 120):
    print_banner()

    # Step 1: Initialize Database
    print("[1/7] Initializing SQLite database schema...")
    init_db()
    print("      ✓ Database initialized at: data/expenses.db")

    # Step 2: Ingest Data
    sample_csv_path = os.path.join(ROOT_DIR, "data", "expenses_sample.csv")
    if generate_synthetic or (csv_path is None and not os.path.exists(sample_csv_path)):
        print(f"[2/7] Generating {num_samples} realistic synthetic expense records...")
        raw_df = generate_synthetic_expenses(
            num_records=num_samples,
            output_path=sample_csv_path
        )
        print(f"      ✓ Generated synthetic data and saved to: {sample_csv_path}")
    else:
        target_path = csv_path if csv_path else sample_csv_path
        print(f"[2/7] Loading expense data from: {target_path}...")
        raw_df = load_expense_csv(target_path)
        print(f"      ✓ Loaded {len(raw_df)} raw records.")

    # Step 3: Data Cleaning & Normalization
    print("[3/7] Cleaning and standardizing transaction records...")
    cleaned_df = clean_expense_data(raw_df)
    print(f"      ✓ Sanitized {len(cleaned_df)} valid transactions.")

    # Step 4: Auto-Categorization & SQLite Upsert
    print("[4/7] Applying rule-based categorization & persisting to SQLite...")
    inserted_count = 0
    for _, row in cleaned_df.iterrows():
        final_category = auto_categorize(row["Description"], row["Category"])
        row_inserted = insert_transaction(
            tx_date=row["Date"],
            category_name=final_category,
            amount=row["Amount"],
            payment_method=row["Payment_Method"],
            description=row["Description"],
            account=row.get("Account", "Primary Account")
        )
        if row_inserted:
            inserted_count += 1
    print(f"      ✓ Synchronized {inserted_count} new transactions into SQLite.")

    # Step 5: Perform Analytics & KPIs
    print("[5/7] Computing financial KPIs and aggregations...")
    kpis = calculate_kpis(cleaned_df)
    cat_summary = get_category_summary(cleaned_df)
    monthly_summary = get_monthly_summary(cleaned_df)
    pm_summary = get_payment_method_summary(cleaned_df)
    top_expenses = get_top_expenses(cleaned_df, n=5)

    # Budget Check on latest active month
    latest_month = monthly_summary["Month"].iloc[-1] if not monthly_summary.empty else "2026-11"
    seed_default_budgets(latest_month)
    budget_summary = check_budget_status(cleaned_df, latest_month)
    print("      ✓ Financial metrics successfully calculated.")

    # Step 6: Generate Visualizations
    print("[6/7] Generating publication-quality charts (Matplotlib & Seaborn)...")
    images_dir = os.path.join(ROOT_DIR, "images")
    plots = generate_all_plots(cleaned_df, output_dir=images_dir)
    for plot_name, path in plots.items():
        if path:
            print(f"      ✓ Saved chart: {path}")

    # Step 7: Export Reports
    print("[7/7] Generating audit reports and CSV summaries...")
    csv_rep_path = os.path.join(ROOT_DIR, "reports", "monthly_summary_report.csv")
    txt_rep_path = os.path.join(ROOT_DIR, "reports", "financial_insights.txt")
    generate_csv_report(cleaned_df, csv_rep_path)
    generate_text_report(kpis, cat_summary, monthly_summary, budget_summary, txt_rep_path)
    print(f"      ✓ Summary CSV exported to: {csv_rep_path}")
    print(f"      ✓ Insight Audit Report exported to: {txt_rep_path}")

    # Terminal Dashboard Display
    print("\n" + "=" * 72)
    print("                 📈 FINANCIAL METRICS DASHBOARD")
    print("=" * 72)
    print(f"  Total Inflow (Income)       : ₹{kpis['total_income']:>12,.2f}")
    print(f"  Total Outflow (Expenses)    : ₹{kpis['total_spend']:>12,.2f}")
    print(f"  Net Savings                 : ₹{kpis['net_savings']:>12,.2f}")
    print(f"  Savings Rate                : {kpis['savings_rate_pct']:>11.1f}%")
    print(f"  Average Daily Spend         : ₹{kpis['avg_daily_spend']:>12,.2f}")
    print(f"  Top Spending Category       : {kpis['highest_spending_category']} (₹{kpis['highest_category_amount']:,.2f} | {kpis['highest_category_pct']:.1f}%)")
    print("=" * 72)

    print("\nCATEGORY-WISE BREAKDOWN:")
    print(f"{'Category':<22} | {'Amount (INR)':<14} | {'% Share':<8} | {'Tx Count'}")
    print("-" * 55)
    for _, r in cat_summary.head(7).iterrows():
        print(f"{r['Category']:<22} | ₹{r['Amount']:<13,.2f} | {r['Percentage']:<7.1f}% | {r['Tx_Count']}")

    print("\nMONTHLY CASH FLOW TRAJECTORY:")
    print(f"{'Month':<10} | {'Income (INR)':<13} | {'Expense (INR)':<13} | {'Savings (INR)':<13} | {'Savings %'}")
    print("-" * 62)
    for _, r in monthly_summary.iterrows():
        print(f"{r['Month']:<10} | ₹{r['Income']:<12,.2f} | ₹{r['Expense']:<12,.2f} | ₹{r['Savings']:<12,.2f} | {r['Savings_Rate_Pct']:.1f}%")

    print("\nLATEST MONTH BUDGET MONITOR (" + latest_month + "):")
    print(f"{'Category':<20} | {'Budget':<10} | {'Actual':<10} | {'Variance':<10} | {'Status'}")
    print("-" * 60)
    for _, r in budget_summary.head(6).iterrows():
        print(f"{r['Category']:<20} | ₹{r['Budget_Limit']:<9,.0f} | ₹{r['Actual_Spend']:<9,.0f} | ₹{r['Variance']:<9,.0f} | [{r['Status']}]")

    print("\n" + "=" * 72)
    print("  ✓ End-to-End Pipeline Completed Successfully!")
    print("  💡 Tip: Run 'streamlit run src/app_streamlit.py' to launch interactive UI.")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Personal Expense Tracker Pipeline")
    parser.add_argument("--csv", type=str, default=None, help="Path to input expense CSV file")
    parser.add_argument("--synthetic", action="store_true", help="Generate fresh synthetic dataset")
    parser.add_argument("--samples", type=int, default=120, help="Number of synthetic records to generate")
    args = parser.parse_args()

    run_pipeline(csv_path=args.csv, generate_synthetic=args.synthetic, num_samples=args.samples)
