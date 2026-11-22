"""
app_streamlit.py - Interactive Personal Finance & Expense Analytics Dashboard
Features:
- Live CSV / Bank statement file upload and ingestion
- Interactive date, month, and account filtering
- KPI metric cards (Total Spend, Income, Net Savings, Daily Velocity)
- Category-wise breakdown & Donut distribution
- Monthly Cash Flow & Trend analysis
- Category Budget monitoring with dynamic progress meters
- Manual transaction quick-entry form writing directly to SQLite database
- Filtered transaction explorer with CSV export
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Ensure src package is in path
sys.path.append(os.path.dirname(__file__))

from database import init_db, insert_transaction, fetch_all_transactions, DEFAULT_DB_PATH
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
from budget import check_budget_status, set_budget

# Page configuration
st.set_page_config(
    page_title="Personal Expense Tracker & Analytics",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished fintech aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data_from_db():
    init_db()
    rows = fetch_all_transactions()
    if not rows:
        # Check if sample csv exists and ingest
        sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "expenses_sample.csv")
        if os.path.exists(sample_path):
            df = pd.read_csv(sample_path)
            df = clean_expense_data(df)
            for _, r in df.iterrows():
                insert_transaction(
                    tx_date=r["Date"],
                    category_name=r["Category"],
                    amount=r["Amount"],
                    payment_method=r["Payment_Method"],
                    description=r["Description"],
                    account=r.get("Account", "Primary Account")
                )
            rows = fetch_all_transactions()
    
    if rows:
        df = pd.DataFrame(rows)
        df = df.rename(columns={
            "tx_date": "Date",
            "category": "Category",
            "amount": "Amount",
            "payment_method": "Payment_Method",
            "description": "Description",
            "account": "Account"
        })
        return clean_expense_data(df)
    return pd.DataFrame(columns=["Date", "Category", "Amount", "Payment_Method", "Description", "Account"])


# Load Transactions
df = load_data_from_db()

# ----------------- SIDEBAR -----------------
st.sidebar.markdown("### ⚙️ Navigation & Ingestion")

# File Uploader
uploaded_file = st.sidebar.file_uploader("📥 Ingest Bank / Expense CSV", type=["csv"])
if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        cleaned_up = clean_expense_data(raw_df)
        inserted_count = 0
        for _, row in cleaned_up.iterrows():
            cat = auto_categorize(row["Description"], row["Category"])
            if insert_transaction(
                tx_date=row["Date"],
                category_name=cat,
                amount=row["Amount"],
                payment_method=row["Payment_Method"],
                description=row["Description"],
                account=row.get("Account", "Manual Upload")
            ):
                inserted_count += 1
        st.sidebar.success(f"✓ Successfully ingested {inserted_count} new transactions!")
        st.cache_data.clear()
        df = load_data_from_db()
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")

# Filters
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filters")

if not df.empty:
    df["Month"] = df["Date"].astype(str).str.slice(0, 7)
    
    all_months = sorted(df["Month"].unique())
    selected_month = st.sidebar.selectbox("Select Month", ["All Months"] + all_months, index=len(all_months))
    
    all_accounts = sorted(df["Account"].unique())
    selected_accounts = st.sidebar.multiselect("Select Accounts", all_accounts, default=all_accounts)
    
    # Apply Filtering
    filtered_df = df[df["Account"].isin(selected_accounts)].copy()
    if selected_month != "All Months":
        filtered_df = filtered_df[filtered_df["Month"] == selected_month]
else:
    filtered_df = df.copy()
    selected_month = "All Months"

# ----------------- HEADER & KPIS -----------------
st.markdown('<div class="main-header">💸 Personal Expense Tracker & Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Personal finance health metrics, automated categorization, and budget variance monitoring.</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.info("No transaction records available. Upload a CSV or use the Manual Entry form below.")
else:
    kpis = calculate_kpis(filtered_df)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Income", f"₹{kpis['total_income']:,.0f}")
    col2.metric("Total Spend", f"₹{kpis['total_spend']:,.0f}")
    col3.metric(
        "Net Savings",
        f"₹{kpis['net_savings']:,.0f}",
        delta=f"{kpis['savings_rate_pct']:.1f}% Savings Rate",
        delta_color="normal" if kpis['net_savings'] >= 0 else "inverse"
    )
    col4.metric("Avg Daily Spend", f"₹{kpis['avg_daily_spend']:,.0f}")
    col5.metric("Top Category", kpis['highest_spending_category'])

    st.markdown("---")

    # ----------------- ANALYTICS TABS -----------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Category Analysis",
        "📈 Monthly Trends",
        "🎯 Budget Monitoring",
        "📋 Transactions Explorer",
        "➕ Manual Entry"
    ])

    with tab1:
        st.subheader("Category-Wise Spend Distribution")
        cat_df = get_category_summary(filtered_df)
        pm_df = get_payment_method_summary(filtered_df)

        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown("##### Total Spending by Category (INR)")
            if not cat_df.empty:
                chart_data = cat_df.set_index("Category")["Amount"]
                st.bar_chart(chart_data)
        with c2:
            st.markdown("##### Payment Method Share")
            if not pm_df.empty:
                st.dataframe(
                    pm_df[["Payment_Method", "Amount", "Percentage"]].style.format({
                        "Amount": "₹{:,.2f}",
                        "Percentage": "{:.1f}%"
                    }),
                    use_container_width=True
                )

        st.markdown("##### Top Individual Expenses")
        top_tx = get_top_expenses(filtered_df, n=5)
        st.dataframe(
            top_tx.style.format({"Amount": "₹{:,.2f}"}),
            use_container_width=True
        )

    with tab2:
        st.subheader("Cash Flow & Monthly Trajectory")
        m_df = get_monthly_summary(df)  # Show all-time for trend
        if not m_df.empty:
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown("##### Income vs Expense Evolution")
                st.line_chart(m_df.set_index("Month")[["Income", "Expense"]])
            with c2:
                st.markdown("##### Month-over-Month Savings Ledger")
                st.dataframe(
                    m_df.style.format({
                        "Income": "₹{:,.2f}",
                        "Expense": "₹{:,.2f}",
                        "Savings": "₹{:,.2f}",
                        "Savings_Rate_Pct": "{:.1f}%"
                    }),
                    use_container_width=True
                )

        st.markdown("##### Daily Spending Velocity")
        daily_df = get_daily_spending_trend(filtered_df)
        if not daily_df.empty:
            st.line_chart(daily_df.set_index("Date")[["Amount", "Rolling_7D_Avg"]])

    with tab3:
        st.subheader("Category Budgets & Variance Analysis")
        eval_month = selected_month if selected_month != "All Months" else sorted(df["Month"].unique())[-1]
        st.info(f"Showing budget tracking for month: **{eval_month}**")

        b_df = check_budget_status(df, eval_month)
        
        # Display alert banners for overspent categories
        overspent = b_df[b_df["Status"] == "EXCEEDED"]
        if not overspent.empty:
            cats = ", ".join(overspent["Category"].tolist())
            st.error(f"⚠️ Budget Breached! You have exceeded your budget limits in: **{cats}**")

        for _, r in b_df.iterrows():
            if r["Budget_Limit"] > 0:
                pct = min(1.0, float(r["Actual_Spend"]) / float(r["Budget_Limit"]))
                col_name, col_prog, col_val = st.columns([2, 5, 2])
                col_name.write(f"**{r['Category']}**")
                col_prog.progress(pct)
                col_val.write(f"₹{r['Actual_Spend']:,.0f} / ₹{r['Budget_Limit']:,.0f} ({r['Pct_Utilized']}%)")

        st.markdown("---")
        st.markdown("##### ⚙️ Update Category Budget Limit")
        with st.form("set_budget_form"):
            b_cat = st.selectbox("Category", sorted(b_df["Category"].unique()))
            b_val = st.number_input("Monthly Limit (INR ₹)", min_value=100.0, max_value=500000.0, value=5000.0, step=500.0)
            b_sub = st.form_submit_button("Save Budget Limit")
            if b_sub:
                set_budget(eval_month, b_cat, b_val)
                st.success(f"✓ Set {eval_month} budget for {b_cat} to ₹{b_val:,.0f}")
                st.rerun()

    with tab4:
        st.subheader("Search & Export Transactions")
        search_query = st.text_input("🔍 Search description, category, or payment method", "")
        
        display_df = filtered_df.copy()
        if search_query:
            q = search_query.lower()
            display_df = display_df[
                display_df["Description"].str.lower().str.contains(q, na=False) |
                display_df["Category"].str.lower().str.contains(q, na=False) |
                display_df["Payment_Method"].str.lower().str.contains(q, na=False)
            ]

        display_df["Date"] = display_df["Date"].astype(str).str.slice(0, 10)
        st.dataframe(
            display_df[["Date", "Category", "Amount", "Payment_Method", "Description", "Account"]]
            .style.format({"Amount": "₹{:,.2f}"}),
            use_container_width=True
        )

        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Transactions as CSV",
            data=csv_data,
            file_name=f"expenses_{selected_month}.csv",
            mime="text/csv"
        )

    with tab5:
        st.subheader("➕ Record Manual Transaction")
        with st.form("manual_entry_form", clear_on_submit=True):
            m_date = st.date_input("Transaction Date")
            m_desc = st.text_input("Merchant / Description", placeholder="e.g., Grocery store, Coffee, Salary")
            m_amt = st.number_input("Amount (INR ₹)", min_value=1.0, max_value=1000000.0, value=250.0, step=10.0)
            m_cat = st.selectbox("Category (Optional auto-detect)", [
                "Auto-Detect", "Groceries", "Food & Dining", "Rent & Housing", "Utilities",
                "Transportation", "Entertainment", "Shopping", "Health & Fitness",
                "Subscriptions", "Income", "Miscellaneous"
            ])
            m_pm = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"])
            m_acc = st.selectbox("Account", ["HDFC Bank", "ICICI Bank", "Credit Card", "Cash Wallet", "Other"])
            
            submit_tx = st.form_submit_button("Record Transaction")
            if submit_tx:
                final_cat = auto_categorize(m_desc) if m_cat == "Auto-Detect" else m_cat
                success = insert_transaction(
                    tx_date=str(m_date),
                    category_name=final_cat,
                    amount=m_amt,
                    payment_method=m_pm,
                    description=m_desc,
                    account=m_acc
                )
                if success:
                    st.success(f"✓ Recorded transaction: {m_desc} (₹{m_amt:,.2f} -> {final_cat})")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("Transaction might be duplicate or could not be inserted.")
