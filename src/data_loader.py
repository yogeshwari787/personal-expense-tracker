"""
data_loader.py - Expense Data Ingestion & Synthetic Dataset Generator
Supports reading CSV/Excel files and generating realistic synthetic personal finance data.
"""

import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd


def generate_synthetic_expenses(
    num_records: int = 120,
    start_date: str = "2026-08-01",
    end_date: str = "2026-11-20",
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Generates a realistic synthetic personal expense dataset.
    Simulates real-world expense distributions across categories, merchants, and payment methods.
    """
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    days_range = (end_dt - start_dt).days

    merchants_by_category = {
        "Groceries": [
            ("D-Mart Monthly Provisions", (1500, 4500)),
            ("Zepto Quick Delivery", (200, 800)),
            ("Blinkit Fresh Vegetables", (250, 950)),
            ("BigBasket Weekly Groceries", (800, 2200)),
            ("Local Kirana Store", (150, 600))
        ],
        "Food & Dining": [
            ("Swiggy Biryani Dinner", (280, 650)),
            ("Zomato Office Lunch", (220, 500)),
            ("Starbucks / Third Wave Coffee", (250, 450)),
            ("Domino's Weekend Pizza", (400, 900)),
            ("Campus Cafeteria Snacks", (60, 180)),
            ("Weekend Fine Dining Restaurant", (1200, 2800))
        ],
        "Rent & Housing": [
            ("Monthly Apartment Rent Payment", (12000, 14000)),
            ("Society Maintenance Fee", (1500, 2500))
        ],
        "Utilities": [
            ("BESCOM Electricity Bill", (900, 1600)),
            ("Jio Fiber Broadband 100Mbps", (699, 999)),
            ("Mobile Postpaid Recharge", (399, 799)),
            ("Water Supply & LPG Cylinder", (500, 1100))
        ],
        "Transportation": [
            ("Uber Cab to Campus / Office", (180, 550)),
            ("Ola Auto Commute", (90, 220)),
            ("Metro Smart Card Recharge", (200, 500)),
            ("Two-Wheeler Petrol Refuel", (300, 750))
        ],
        "Entertainment": [
            ("PVR Cinemas Movie Tickets & Popcorn", (500, 1200)),
            ("Netflix Standard Subscription", (499, 649)),
            ("BookMyShow Standup Comedy", (600, 1500)),
            ("Steam Video Game Purchase", (400, 1800))
        ],
        "Shopping": [
            ("Amazon Electronics & Books", (600, 3500)),
            ("Flipkart Fashion Apparel", (800, 2800)),
            ("Myntra Shoes & Athleisure", (1200, 3200)),
            ("Campus Bookstore Stationery", (200, 800))
        ],
        "Health & Fitness": [
            ("Gym / Fitness Center Membership", (1200, 2000)),
            ("Apollo Pharmacy Prescription Medicines", (250, 900)),
            ("Sports Complex Court Booking", (300, 600))
        ],
        "Subscriptions": [
            ("Spotify Premium Student Plan", (119, 119)),
            ("Google One Cloud Storage", (130, 210)),
            ("GitHub Copilot / Developer Tools", (850, 1000))
        ]
    }

    payment_methods = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]
    method_weights = [0.50, 0.25, 0.12, 0.08, 0.05]

    accounts = ["HDFC Bank", "ICICI Bank", "Credit Card", "Cash Wallet"]
    account_weights = [0.55, 0.20, 0.17, 0.08]

    records = []

    # 1. Inject recurring monthly income on the 1st of each month
    current_dt = start_dt
    while current_dt <= end_dt:
        if current_dt.day == 1:
            records.append({
                "Date": current_dt.strftime("%Y-%m-%d"),
                "Category": "Income",
                "Amount": round(random.choice([45000.0, 48000.0, 50000.0]), 2),
                "Payment_Method": "Net Banking",
                "Description": "Monthly Stipend / Salary Credit",
                "Account": "HDFC Bank"
            })
            # Also inject monthly rent on the 2nd
            rent_dt = current_dt + timedelta(days=1)
            records.append({
                "Date": rent_dt.strftime("%Y-%m-%d"),
                "Category": "Rent & Housing",
                "Amount": 12000.00,
                "Payment_Method": "Net Banking",
                "Description": "Apartment Rent Payment",
                "Account": "HDFC Bank"
            })
        current_dt += timedelta(days=1)

    # 2. Inject distributed daily/weekly expenses
    categories = list(merchants_by_category.keys())
    cat_weights = [0.22, 0.28, 0.05, 0.08, 0.14, 0.07, 0.09, 0.04, 0.03]

    for _ in range(num_records):
        random_days = random.randint(0, days_range)
        tx_dt = start_dt + timedelta(days=random_days)
        cat = random.choices(categories, weights=cat_weights, k=1)[0]
        desc, (low_amt, high_amt) = random.choice(merchants_by_category[cat])
        amt = round(random.uniform(low_amt, high_amt), 2)
        pm = random.choices(payment_methods, weights=method_weights, k=1)[0]
        acc = random.choices(accounts, weights=account_weights, k=1)[0]

        records.append({
            "Date": tx_dt.strftime("%Y-%m-%d"),
            "Category": cat,
            "Amount": amt,
            "Payment_Method": pm,
            "Description": desc,
            "Account": acc
        })

    df = pd.DataFrame(records)
    df = df.sort_values(by="Date").reset_index(drop=True)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)

    return df


def load_expense_csv(file_path: str) -> pd.DataFrame:
    """Loads expense transactions from a CSV file into a pandas DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Expense CSV file not found: {file_path}")
    return pd.read_csv(file_path)

