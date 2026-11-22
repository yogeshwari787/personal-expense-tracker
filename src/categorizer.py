"""
categorizer.py - Rule-Based Smart Auto-Categorization Engine
Automatically classifies descriptions into standard expense/income categories
using regular expressions and pattern matching.
"""

import re
from typing import Optional


CATEGORIZATION_RULES = {
    "Income": [
        r"salary", r"stipend", r"bonus", r"freelance", r"dividend",
        r"interest payout", r"reimbursement", r"refund", r"cashback"
    ],
    "Rent & Housing": [
        r"rent", r"apartment", r"flat", r"hostel", r"pg\b",
        r"maintenance fee", r"society charge"
    ],
    "Groceries": [
        r"d-mart", r"dmart", r"big bazaar", r"reliance fresh", r"smart bazaar",
        r"zepto", r"blinkit", r"instamart", r"bigbasket", r"nature basket",
        r"grocery", r"supermarket", r"provisions", r"vegetables", r"fruits"
    ],
    "Food & Dining": [
        r"swiggy", r"zomato", r"restaurant", r"cafe", r"coffee",
        r"starbucks", r"domino'?s", r"pizza", r"burger", r"mcdonald",
        r"kfc", r"subway", r"biryani", r"tea", r"chai", r"canteen"
    ],
    "Utilities": [
        r"electricity", r"bescom", r"water bill", r"lpg", r"gas",
        r"broadband", r"wifi", r"jio fiber", r"airtel", r"postpaid",
        r"recharge", r"utility", r"dth"
    ],
    "Transportation": [
        r"uber", r"ola", r"rapido", r"auto", r"metro", r"bus pass",
        r"petrol", r"diesel", r"fuel", r"irctc", r"train", r"flight",
        r"toll", r"cab"
    ],
    "Entertainment": [
        r"netflix", r"amazon prime", r"hotstar", r"bookmyshow",
        r"pvr", r"inox", r"cinema", r"movie", r"concert", r"steam",
        r"gaming", r"theatre"
    ],
    "Shopping": [
        r"amazon", r"flipkart", r"myntra", r"ajio", r"zara",
        r"uniqlo", r"h&m", r"electronics", r"clothing", r"shoes",
        r"apparel", r"bookstore"
    ],
    "Health & Fitness": [
        r"gym", r"fitness", r"cult\.fit", r"pharmacy", r"apollo",
        r"medicine", r"doctor", r"hospital", r"clinic", r"vitamins",
        r"lab test", r"badminton"
    ],
    "Subscriptions": [
        r"spotify", r"youtube premium", r"apple music", r"icloud",
        r"google one", r"github copilot", r"chatgpt", r"coursera",
        r"udemy"
    ]
}


def auto_categorize(description: str, current_category: Optional[str] = None) -> str:
    """
    Classifies a transaction description into a standard category.
    If current_category is already specific (not Uncategorized/Other), it is preserved.
    """
    if current_category and current_category.strip() not in ["", "Uncategorized", "Other", "Unknown"]:
        return current_category.strip()

    desc_lower = str(description).lower()

    for category, patterns in CATEGORIZATION_RULES.items():
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                return category

    return "Miscellaneous"
