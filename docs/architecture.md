# System Architecture & Technical Design

## 1. High-Level Architecture Overview

The **Personal Expense Tracker with Data Visualization** implements a decoupled, modular ETL and Analytical pipeline. It follows modern data engineering design patterns to ingest, normalize, persist, aggregate, visualize, and audit personal financial transactions.

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

## 2. Database Schema (SQLite)

### Table: `categories`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique Category ID |
| `name` | TEXT | UNIQUE, NOT NULL | Category label (e.g., Groceries, Rent) |
| `category_type` | TEXT | DEFAULT 'Expense' | 'Expense' or 'Income' |

### Table: `transactions`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique Transaction ID |
| `tx_date` | TEXT | NOT NULL | ISO date string (`YYYY-MM-DD`) |
| `category_id` | INTEGER | FOREIGN KEY REFERENCES categories(id) | Associated category |
| `amount` | REAL | NOT NULL | Transaction absolute amount |
| `payment_method` | TEXT | NOT NULL | UPI, Credit Card, Debit Card, Cash, etc. |
| `description` | TEXT | | Merchant / note particulars |
| `account` | TEXT | DEFAULT 'Primary Account' | Account origin (e.g., HDFC, Cash) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |

*Constraint*: `UNIQUE(tx_date, description, amount, payment_method)` prevents accidental double counting.

### Table: `budgets`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique Budget ID |
| `month` | TEXT | NOT NULL | Target billing month (`YYYY-MM`) |
| `category_name` | TEXT | NOT NULL | Monitored category |
| `limit_amount` | REAL | NOT NULL | Monthly budget threshold in INR |

*Constraint*: `UNIQUE(month, category_name)` ensures one cap per category per month.

## 3. Data Flow Step-by-Step

1. **Ingestion**: Raw CSV or manual data is read into memory using pandas or Python standard loaders.
2. **Standardization**: Field names are mapped via a semantic synonym dictionary (`narration`, `note`, `merchant` -> `Description`).
3. **Validation**: Dates are converted to ISO format (`YYYY-MM-DD`); amounts are converted to positive floating-point numbers.
4. **Classification**: Uncategorized transactions are matched against regular expression dictionaries (e.g. `swiggy`, `zomato` -> `Food & Dining`).
5. **Persistence**: Transactions are upserted into SQLite using `INSERT OR IGNORE` to guarantee idempotency.
6. **Analytics Execution**: Group-by operations calculate category totals, monthly cash flows, and budget variances.
7. **Rendering & Export**: Static charts are saved in `images/`, audit reports in `reports/`, and dynamic metrics are served via Streamlit.

