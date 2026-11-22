"""
data_cleaner.py - Data Preprocessing & Normalization
Cleans raw transaction entries, converts dates, validates numeric amounts,
standardizes payment methods, and removes duplicate transactions.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Any


COLUMN_MAPPINGS = {
    # Date variants
    "date": "Date",
    "tx_date": "Date",
    "transaction_date": "Date",
    "timestamp": "Date",
    # Description variants
    "description": "Description",
    "narration": "Description",
    "notes": "Description",
    "note": "Description",
    "particulars": "Description",
    "merchant": "Description",
    # Amount variants
    "amount": "Amount",
    "spend": "Amount",
    "expense": "Amount",
    "debit": "Amount",
    # Category variants
    "category": "Category",
    "type": "Category",
    "expense_category": "Category",
    # Payment method variants
    "payment_method": "Payment_Method",
    "payment_mode": "Payment_Method",
    "method": "Payment_Method",
    "mode": "Payment_Method",
    # Account variants
    "account": "Account",
    "bank": "Account",
    "source": "Account"
}

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M"
]


def parse_date_to_iso(val: Any) -> Optional[str]:
    """Parses date string or object into standard ISO format (YYYY-MM-DD)."""
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    if "T" in s:
        s = s.split("T")[0]
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def clean_expense_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes raw expense DataFrame.
    Returns sanitized DataFrame with columns:
    ['Date', 'Category', 'Amount', 'Payment_Method', 'Description', 'Account']
    """
    cleaned = df.copy()

    # 1. Normalize column headers
    renamed_cols = {}
    for col in cleaned.columns:
        norm = str(col).strip().lower().replace(" ", "_")
        if norm in COLUMN_MAPPINGS:
            renamed_cols[col] = COLUMN_MAPPINGS[norm]
    cleaned = cleaned.rename(columns=renamed_cols)

    # Ensure essential columns exist
    if "Date" not in cleaned.columns:
        raise ValueError("Missing required column: Date")
    if "Amount" not in cleaned.columns:
        raise ValueError("Missing required column: Amount")

    # Set default values for optional columns if missing
    if "Category" not in cleaned.columns:
        cleaned["Category"] = "Uncategorized"
    if "Payment_Method" not in cleaned.columns:
        cleaned["Payment_Method"] = "UPI"
    if "Description" not in cleaned.columns:
        cleaned["Description"] = "General Transaction"
    if "Account" not in cleaned.columns:
        cleaned["Account"] = "Primary Account"

    # 2. Date conversion and formatting (cross-version Python safe)
    cleaned["Date"] = cleaned["Date"].apply(parse_date_to_iso)
    cleaned = cleaned.dropna(subset=["Date"])

    # 3. Clean numeric amounts
    # Strip symbols like ₹, $, commas, spaces
    if cleaned["Amount"].dtype == object:
        cleaned["Amount"] = (
            cleaned["Amount"]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
    cleaned["Amount"] = pd.to_numeric(cleaned["Amount"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Amount"])
    cleaned["Amount"] = cleaned["Amount"].abs().round(2)

    # 4. Standardize text strings
    cleaned["Category"] = cleaned["Category"].fillna("Uncategorized").astype(str).str.strip().str.title()
    cleaned["Description"] = cleaned["Description"].fillna("No Description").astype(str).str.strip()
    cleaned["Account"] = cleaned["Account"].fillna("Primary Account").astype(str).str.strip()

    # 5. Standardize Payment Methods
    def standardize_pm(val: str) -> str:
        s = str(val).strip().lower()
        if any(k in s for k in ["upi", "gpay", "phonepe", "paytm"]):
            return "UPI"
        elif any(k in s for k in ["credit", "cc"]):
            return "Credit Card"
        elif any(k in s for k in ["debit", "dc"]):
            return "Debit Card"
        elif any(k in s for k in ["net", "banking", "neft", "rtgs", "imps", "transfer"]):
            return "Net Banking"
        elif "cash" in s:
            return "Cash"
        return "Other"

    cleaned["Payment_Method"] = cleaned["Payment_Method"].apply(standardize_pm)

    # 6. Remove exact duplicate transactions
    cleaned = cleaned.drop_duplicates(subset=["Date", "Description", "Amount", "Payment_Method"]).reset_index(drop=True)

    # 7. Sort by date
    cleaned = cleaned.sort_values(by="Date", ascending=True).reset_index(drop=True)

    return cleaned[["Date", "Category", "Amount", "Payment_Method", "Description", "Account"]]
