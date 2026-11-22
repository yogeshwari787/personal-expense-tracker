# 💸 Personal Expense Tracker with Data Visualization

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0%2B-003B57.svg)](https://www.sqlite.org/)

An industry-oriented, automated personal finance analytics engine and interactive dashboard built in Python. This project ingests transaction records (manual, bank CSVs, or synthetic data), standardizes dirty formats, executes smart rule-based auto-categorization, stores records in a relational SQLite database, computes key financial KPIs, renders publication-quality visualization charts, monitors category budgets, and produces executive monthly audit reports.

---

## 📌 Table of Contents
- [Project Overview](#-project-overview)
- [Problem Statement & Industry Relevance](#-problem-statement--industry-relevance)
- [Core Features](#-core-features)
- [Architecture & Data Pipeline](#-architecture--data-pipeline)
- [Tech Stack](#-tech-stack)
- [Project Folder Structure](#-project-folder-structure)
- [Installation & Setup](#-installation--setup)
- [How to Run the Project](#-how-to-run-the-project)
- [Visualizations & Sample Outputs](#-visualizations--sample-outputs)
- [Executive Financial Insights Report](#-executive-financial-insights-report)
- [Git Proof-of-Work Strategy (Day 1 - Day 6)](#-git-proof-of-work-strategy)
- [Interview Q&A Guide](#-interview-qa-guide)
- [Future Roadmap & Extensions](#-future-roadmap--extensions)
- [License & Contributing](#-license--contributing)

---

## 📖 Project Overview

Financial literacy and automated personal analytics are essential life skills and high-demand industry capabilities. Many individuals—especially students, freelancers, and young professionals—struggle to track their monthly cash flows, frequently overspend on discretionary wants, and lack visibility into their savings rate.

This project delivers a **production-ready ETL (Extract, Transform, Load) and Visualization Pipeline**:
1. **Extract**: Ingests transactions from heterogeneous bank exports, CSV files, or programmatic synthetic data generators.
2. **Transform**: Cleans invalid dates, removes duplicate charges, normalizes amounts, and uses regular expression pattern matching to classify descriptions into categories (Groceries, Utilities, Rent, Dining, etc.).
3. **Load**: Persists normalized data into a lightweight, indexed SQLite database with strict unique constraints.
4. **Analyze**: Calculates savings rates, 7-day daily spending velocity, category concentrations, and budget variance.
5. **Visualize & Report**: Automatically generates high-resolution Matplotlib/Seaborn charts, an interactive Streamlit web dashboard, and exportable CSV and text audit reports.

---

## 🎯 Problem Statement & Industry Relevance

### The Problem
- **Lack of Spending Visibility**: Bank statements are cluttered with unhelpful merchant codes (e.g., `POS 4912 SWIGGY`, `BESCOM BILL 9812`).
- **No Budget Enforcement**: Without active category caps, discretionary expenses compound unnoticed until month-end.
- **Privacy & Security Concerns**: Cloud-based finance trackers often require linking live bank credentials, which many users prefer to avoid.

### Who Benefits?
- **Students**: Manage fixed monthly allowances, minimize food delivery expenses, and maintain emergency funds.
- **Employees & Professionals**: Implement the 50/30/20 budgeting rule (50% Needs, 30% Wants, 20% Savings).
- **Freelancers**: Track variable cash flows, project bonuses, and client reimbursements.
- **Small Businesses**: Audit recurring operational expenses, software subscriptions, and utility bills.

### Industry Relevance (Why Recruiters Care)
This project maps directly to core responsibilities in **Python Developer, Data Analyst, Business Analyst, and Financial Analytics** roles:
- Clean modular architecture (Separation of Concerns).
- Robust schema modeling and SQL queries with SQLite.
- Text parsing, data cleaning, and regular expressions.
- Financial storytelling and metric calculation.
- Interactive dashboard engineering with Streamlit.

---

## ⚡ Core Features

- **Multi-Source Ingestion**: Load custom bank statement CSVs, enter transactions via CLI/web form, or generate realistic synthetic multi-month datasets.
- **Data Sanitization**: Automatically handles currency symbols (`₹`, `$`), inconsistent date formats (`YYYY-MM-DD`, `DD/MM/YYYY`), and deduplication.
- **Rule-Based Smart Categorization**: Instant regex classification for merchants (Swiggy, Zomato, D-Mart, Uber, BESCOM, Netflix, Amazon, etc.).
- **SQLite Database Persistence**: Normalized relational tables for `categories`, `transactions`, and `budgets` with indexing.
- **Automated KPI Engine**:
  - Total Spend & Total Income
  - Net Savings & Savings Rate (%)
  - 7-Day Moving Average Daily Spend
  - Top Spending Category & Merchant
- **Publication-Ready Visualizations**:
  - Horizontal Category Spend Bar Chart
  - Income vs Expense Monthly Line Chart
  - Payment Method Share Donut Chart
  - Daily Spending Timeline with Moving Average
- **Monthly Budget Variance Monitor**: Real-time progress bars and alerts for categories exceeding budget caps.
- **Interactive Streamlit Web Dashboard**: Real-time filtering by billing month, account, or merchant with one-click CSV export.
- **Executive Audit Report**: Automated `.txt` financial health diagnostic with a 0–100 score and actionable recommendations.

---

## 🏗️ Architecture & Data Pipeline

```
+-------------------------------------------------------------------------+
|                              DATA INPUT LAYER                           |
|  - Manual CLI/Form Entry     - Bank Statements (CSV)   - Synthetic Data |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                        CLEANING & INGESTION LAYER                       |
|  - Header Normalization     - Date Sanitization (ISO 8601)              |
|  - Amount Type Casting      - Duplicate Deduplication                   |
|  - Payment Method Standard  - Missing Value Imputation                  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                   INTELLIGENT CATEGORIZATION ENGINE                     |
|  - Keyword & Regex Matcher  - Category Fallback Strategy                |
|  - Income vs Expense Rule   - Future Extensibility (ML/Naive Bayes)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                      DATA PERSISTENCE LAYER (SQLite)                    |
|  - Normalized Tables: categories, transactions, budgets                 |
|  - Relational Integrity: Foreign Keys, Unique Constraints               |
|  - Analytical Query Indexes: tx_date, category_id, month                |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                        ANALYTICS & KPI ENGINE                           |
|  - Total Spend & Inflow     - Net Savings & Savings Rate (%)            |
|  - Category Aggregation     - Monthly Trajectory Analysis               |
|  - Daily Velocity (7D MA)   - Budget Variance & Overspend Alerts        |
+-------------------------------------------------------------------------+
                                    |
                 +------------------+------------------+
                 |                                     |
                 v                                     v
+----------------------------------+ +------------------------------------+
|       VISUALIZATION LAYER        | |         REPORTING & UI LAYER       |
|  - Matplotlib & Seaborn Charts   | |  - Streamlit Web Dashboard         |
|  - Category Bar & Donut Charts   | |  - Monthly CSV Export              |
|  - Monthly Trend Area Plots      | |  - Comprehensive TXT Audit Report  |
|  - Payment Share Visuals         | |  - Actionable Savings Tips         |
+----------------------------------+ +------------------------------------+
```

---

## 💻 Tech Stack

| Category | Technology / Library | Purpose |
|---|---|---|
| **Core Language** | Python 3.9+ | Main programming language |
| **Data Manipulation** | Pandas & NumPy | High-performance tabular transformation and aggregations |
| **Database** | SQLite3 | Local ACID-compliant relational persistence |
| **Data Visualization** | Matplotlib & Seaborn | Static high-DPI chart rendering |
| **Interactive Dashboard**| Streamlit | Web application UI for interactive exploration |
| **Pattern Matching** | Python `re` (Regex) | Keyword-based auto-categorization |
| **Export Formats** | CSV, OpenPyXL, Text | Report and audit document generation |

---

## 📁 Project Folder Structure

```
Personal-Expense-Tracker-Visualization/
│
├── data/
│   ├── expenses_sample.csv          # Realistic 4-month sample dataset
│   └── expenses.db                  # Local SQLite database file
│
├── docs/
│   └── architecture.md              # Detailed technical design & DB schema
│
├── images/                          # Publication-quality charts
│   ├── category_distribution.png    # Category spend horizontal bar chart
│   ├── daily_spending.png           # Daily spending timeline + 7D moving avg
│   ├── monthly_trend.png            # Income vs Expense month-over-month trend
│   └── payment_methods.png          # Donut chart of payment method distribution
│
├── notebooks/
│   └── exploratory_data_analysis.ipynb # Step-by-step EDA Jupyter Notebook
│
├── outputs/                         # Intermediate analytical extracts
│
├── reports/                         # Generated audit summaries
│   ├── financial_insights.txt       # Executive diagnostic audit report
│   └── monthly_summary_report.csv   # Aggregated category metrics
│
├── src/                             # Modular Python package
│   ├── __init__.py                  # Package initializer
│   ├── analytics.py                 # KPI and financial aggregation algorithms
│   ├── app_streamlit.py             # Streamlit interactive web dashboard
│   ├── budget.py                    # Monthly budget limits & variance checker
│   ├── categorizer.py               # Regex-driven auto-categorization engine
│   ├── data_cleaner.py              # Data cleaning and normalization rules
│   ├── data_loader.py               # CSV reader and synthetic data generator
│   ├── database.py                  # SQLite schema definitions & CRUD methods
│   ├── reporter.py                  # Audit report generators (CSV & TXT)
│   └── visualizer.py                # Matplotlib & Seaborn chart generator
│
├── .gitignore                       # Standard Python & OS ignore rules
├── main.py                          # End-to-end command-line pipeline driver
├── README.md                        # Master project documentation
└── requirements.txt                 # Project dependencies
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9, 3.10, 3.11, 3.12, or 3.14 installed.
- Git installed.

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Personal-Expense-Tracker-Visualization.git
cd Personal-Expense-Tracker-Visualization
```

### Step 2: Create a Virtual Environment

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Project

### 1. Execute the Automated CLI Pipeline
Run the complete pipeline from data ingestion to chart generation:
```bash
python main.py
```

### 2. Generate a Fresh Synthetic Dataset
Simulate a brand-new user with 150 randomized transactions:
```bash
python main.py --synthetic --samples 150
```

### 3. Analyze a Custom Bank CSV File
Ingest your own bank or expense CSV:
```bash
python main.py --csv /path/to/my_bank_statement.csv
```

### 4. Launch the Interactive Streamlit Web Dashboard
```bash
streamlit run src/app_streamlit.py
```
Open your browser at `http://localhost:8501` to view interactive KPI cards, budget progress meters, and transaction filters.

---

## 📊 Visualizations & Sample Outputs

The automated visualizer generates publication-grade visualizations in `images/`:

| Chart | Description | Preview |
|---|---|---|
| **Category Distribution** | Horizontal ranking of expenses with INR labels | `images/category_distribution.png` |
| **Monthly Trend** | Trajectory of Income vs Outflow across months | `images/monthly_trend.png` |
| **Payment Share** | Donut breakdown of UPI, Card, Net Banking & Cash | `images/payment_methods.png` |
| **Daily Spending Velocity** | Daily transaction bars + 7-day moving average | `images/daily_spending.png` |

---

## 📄 Executive Financial Insights Report

When `main.py` runs, it generates an audit report at `reports/financial_insights.txt`:

```text
========================================================================
       PERSONAL EXPENSE TRACKER - MONTHLY FINANCIAL AUDIT REPORT
========================================================================
Generated On          : 2026-11-22 11:19:03
Financial Health Score: 90/100 -> EXCELLENT (Strong Savings Discipline)
------------------------------------------------------------------------
1. EXECUTIVE FINANCIAL SUMMARY
------------------------------------------------------------------------
  • Total Income Recorded   : ₹183,000.00
  • Total Expenses Incurred : ₹106,431.50
  • Net Savings             : ₹76,568.50
  • Overall Savings Rate    : 41.8%
  • Average Daily Spend     : ₹950.28
  • Highest Spend Category  : Rent & Housing (₹48,000.00 | 45.1% of total)
  • Total Transactions      : 58 (54 debits, 4 credits)

------------------------------------------------------------------------
2. CATEGORY-WISE SPENDING BREAKDOWN
------------------------------------------------------------------------
Category               | Amount (INR)   | % Share   | Tx Count
------------------------------------------------------------------------
Rent & Housing         | ₹48,000.00     | 45.1    % | 4
Groceries              | ₹17,340.50     | 16.3    % | 8
Shopping               | ₹16,948.00     | 15.9    % | 6
Utilities              | ₹7,147.00      | 6.7     % | 7
Food & Dining          | ₹6,400.00      | 6.0     % | 11
Health & Fitness       | ₹3,650.00      | 3.4     % | 4
Entertainment          | ₹3,397.00      | 3.2     % | 4
Transportation         | ₹3,250.00      | 3.0     % | 9
Subscriptions          | ₹299.00        | 0.3     % | 1

------------------------------------------------------------------------
3. MONTH-OVER-MONTH CASH FLOW
------------------------------------------------------------------------
Month      | Income (INR)   | Expense (INR)  | Savings (INR)  | Savings %
------------------------------------------------------------------------
2026-08    | ₹45,000.00     | ₹27,426.50     | ₹17,573.50     | 39.1%
2026-09    | ₹45,000.00     | ₹26,057.00     | ₹18,943.00     | 42.1%
2026-10    | ₹48,000.00     | ₹30,609.00     | ₹17,391.00     | 36.2%
2026-11    | ₹45,000.00     | ₹22,339.00     | ₹22,661.00     | 50.4%

------------------------------------------------------------------------
4. BUDGET VARIANCE & OVERSPEND MONITOR
------------------------------------------------------------------------
Category             | Budget      | Actual      | Variance    | Status
------------------------------------------------------------------------
Rent & Housing       | ₹12,500     | ₹12,000     | ₹500        | [WARNING]
Groceries            | ₹5,000      | ₹4,100      | ₹900        | [WITHIN LIMIT]
Shopping             | ₹4,000      | ₹2,100      | ₹1,900      | [WITHIN LIMIT]
Utilities            | ₹2,500      | ₹1,180      | ₹1,320      | [WITHIN LIMIT]
Food & Dining        | ₹3,000      | ₹1,030      | ₹1,970      | [WITHIN LIMIT]
Transportation       | ₹2,000      | ₹730        | ₹1,270      | [WITHIN LIMIT]

------------------------------------------------------------------------
5. ACTIONABLE PERSONAL FINANCE RECOMMENDATIONS
------------------------------------------------------------------------
  [✓] All monitored categories remained within planned budgetary limits.
  [✓] Follow the 50/30/20 Rule: 50% Needs, 30% Wants, 20% Savings.
========================================================================
```

---

## 📅 Git Proof-of-Work Strategy

To demonstrate consistent, industry-standard engineering habits on GitHub, follow this 6-day commit strategy:

| Day | Milestone Goal | Files Committed | Suggested Commit Message |
|---|---|---|---|
| **Day 1** | Project Setup & Architecture | `requirements.txt`, `.gitignore`, `docs/architecture.md` | `feat: initialize project structure, architecture spec, and requirements` |
| **Day 2** | Database & Data Generator | `src/database.py`, `src/data_loader.py`, `data/expenses_sample.csv` | `feat(db): implement SQLite schema, CRUD operations, and synthetic data generator` |
| **Day 3** | Cleaning & Categorizer | `src/data_cleaner.py`, `src/categorizer.py` | `feat(etl): implement data sanitization and regex-based categorization engine` |
| **Day 4** | KPI Engine & Visualizer | `src/analytics.py`, `src/visualizer.py`, `images/*.png` | `feat(analytics): add financial KPI engine and publish matplotlib charts` |
| **Day 5** | Budget Tracker & Streamlit | `src/budget.py`, `src/app_streamlit.py` | `feat(ui): add budget variance monitoring and interactive streamlit dashboard` |
| **Day 6** | CLI Driver, Reports & Docs | `main.py`, `src/reporter.py`, `reports/*`, `README.md` | `docs: complete production README, automated audit reporter, and execution driver` |

---

## 💼 Interview Q&A Guide

### Q1: Can you explain your Personal Expense Tracker project?
- **HR Explanation**: I built a personal financial intelligence system in Python that helps users track where their money goes. It reads daily transactions from bank statements or manual entries, automatically organizes them into categories like rent and groceries, checks if the user is sticking to their budget, and displays clear visual charts and monthly reports.
- **Technical Explanation**: I architected a modular ETL and analytics pipeline in Python. The ingestion layer reads heterogeneous CSV files and standardizes schemas. A regex-based classification engine auto-categorizes unstructured merchant descriptions. Normalized data is persisted in SQLite with relational integrity and indexing. An analytics engine computes KPIs (savings rate, 7-day rolling spend velocity, budget variances), while Matplotlib/Seaborn and Streamlit provide static and interactive reporting layers.

### Q2: Why did you choose SQLite over simple CSV storage or a heavier database like PostgreSQL?
- **HR Explanation**: SQLite is lightweight and self-contained. It requires zero server setup while still offering full database protection against corrupted data.
- **Technical Explanation**: While CSVs work for small flat files, they lack relational integrity, atomic transactions (ACID compliance), foreign key validation, and indexing. SQLite provides zero-configuration, serverless relational persistence that easily handles tens of thousands of transactions with sub-millisecond query performance, while remaining portable for any user or recruiter cloning the repo.

### Q3: How does the auto-categorization engine work?
- **HR Explanation**: It looks at the text in each transaction (like "Swiggy" or "Uber") and recognizes which bucket it belongs to (Food & Dining or Transportation).
- **Technical Explanation**: It uses a priority regex mapping dictionary where categories are keys and compiled patterns are values. The algorithm checks incoming transaction descriptions against targeted regex patterns. If a match is found, it assigns the category; if none match, it gracefully defaults to "Miscellaneous", allowing manual override without crashing the pipeline.

### Q4: How do you handle messy or inconsistent date formats?
- **Technical Explanation**: Real bank statements use varying conventions (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, ISO timestamps). I implemented a cross-platform parser function that attempts ordered format matching using Python's `datetime.strptime`, standardizes them to ISO-8601 (`YYYY-MM-DD`), and drops corrupt rows.

### Q5: How do you prevent duplicate transactions from being ingested?
- **Technical Explanation**: I implemented a database-level composite unique constraint on `(tx_date, description, amount, payment_method)`. Ingestion uses `INSERT OR IGNORE`, ensuring idempotent upserts even if the user uploads overlapping monthly statement files.

---

## 🔮 Future Roadmap & Extensions

- [ ] **Receipt OCR Integration**: Add Tesseract OCR to scan paper receipts and supermarket bills directly into transactions.
- [ ] **SMS / Email Alerts**: Trigger automated email notifications whenever a category budget reaches 90% utilization.
- [ ] **Machine Learning Classifier**: Train a Multinomial Naive Bayes / TF-IDF classifier on historical user overrides to improve categorization accuracy.
- [ ] **Multi-Currency Support**: Integrate free currency exchange APIs (e.g., Fixer.io) to support international travel expenses.
- [ ] **Recurring Subscription Detector**: Automatically detect monthly recurring charges (e.g., Netflix, Spotify, gym) and alert the user about unused subscriptions.

---

## 📜 License & Author

- **Author**: Student Developer ([GitHub Profile](https://github.com/))
- **Project**: Industry Proof-of-Work Portfolio Project
- **License**: Licensed under the [MIT License](LICENSE).
