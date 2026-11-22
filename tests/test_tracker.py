"""
test_tracker.py - Automated Unit Tests for Expense Tracker Pipeline
Tests data cleaning, auto-categorization, SQLite persistence, and KPI analytics.
"""

import unittest
import os
import sys
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import tempfile
import sqlite3

# Add src to path
SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
sys.path.insert(0, SRC_DIR)

from data_cleaner import clean_expense_data, parse_date_to_iso
from categorizer import auto_categorize
from analytics import calculate_kpis, get_category_summary
from database import init_db, insert_transaction, fetch_all_transactions
from budget import check_budget_status, set_budget


class TestExpenseTracker(unittest.TestCase):

    def test_parse_date_to_iso(self):
        """Test robust multi-format date parsing."""
        self.assertEqual(parse_date_to_iso("2026-11-20"), "2026-11-20")
        self.assertEqual(parse_date_to_iso("15/09/2026"), "2026-09-15")
        self.assertEqual(parse_date_to_iso("08-10-2026"), "2026-10-08")
        self.assertIsNone(parse_date_to_iso(None))

    def test_clean_expense_data(self):
        """Test column normalization and currency symbol removal."""
        raw_data = {
            "tx_date": ["2026-08-01", "2026-08-02"],
            "particulars": ["Swiggy Dinner", "Grocery Store"],
            "debit": ["₹450.50", "1,200.00"],
            "mode": ["gpay", "cc"]
        }
        df = pd.DataFrame(raw_data)
        cleaned = clean_expense_data(df)

        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned["Amount"].iloc[0], 450.50)
        self.assertEqual(cleaned["Amount"].iloc[1], 1200.00)
        self.assertEqual(cleaned["Payment_Method"].iloc[0], "UPI")
        self.assertEqual(cleaned["Payment_Method"].iloc[1], "Credit Card")

    def test_auto_categorize(self):
        """Test regex-based categorization engine."""
        self.assertEqual(auto_categorize("Swiggy biryani delivery"), "Food & Dining")
        self.assertEqual(auto_categorize("Uber cab ride to college"), "Transportation")
        self.assertEqual(auto_categorize("BESCOM electricity bill"), "Utilities")
        self.assertEqual(auto_categorize("D-Mart monthly provisions"), "Groceries")
        self.assertEqual(auto_categorize("Monthly stipend salary credit"), "Income")
        self.assertEqual(auto_categorize("Random unknown store XYZ"), "Miscellaneous")

    def test_database_and_analytics(self):
        """Test SQLite insertion and financial KPI calculation."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            init_db(db_path)
            # Insert test records
            insert_transaction("2026-11-01", "Income", 50000.0, "Net Banking", "Monthly Salary", db_path=db_path)
            insert_transaction("2026-11-02", "Rent & Housing", 15000.0, "Net Banking", "Apartment Rent", db_path=db_path)
            insert_transaction("2026-11-03", "Groceries", 5000.0, "UPI", "D-Mart Grocery", db_path=db_path)

            rows = fetch_all_transactions(db_path)
            self.assertEqual(len(rows), 3)

            test_df = pd.DataFrame(rows).rename(columns={
                "tx_date": "Date", "category": "Category", "amount": "Amount",
                "payment_method": "Payment_Method", "description": "Description"
            })
            kpis = calculate_kpis(test_df)

            self.assertEqual(kpis["total_income"], 50000.0)
            self.assertEqual(kpis["total_spend"], 20000.0)
            self.assertEqual(kpis["net_savings"], 30000.0)
            self.assertEqual(kpis["savings_rate_pct"], 60.0)
            self.assertEqual(kpis["highest_spending_category"], "Rent & Housing")

            # Budget check
            set_budget("2026-11", "Rent & Housing", 12000.0, db_path=db_path)
            budget_df = check_budget_status(test_df, "2026-11", db_path=db_path)
            rent_row = budget_df[budget_df["Category"] == "Rent & Housing"].iloc[0]
            self.assertEqual(rent_row["Status"], "EXCEEDED")
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


if __name__ == "__main__":
    unittest.main()
