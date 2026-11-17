# Finance Data Analysis & AI Automation Dashboard

An enterprise-grade, fully autonomous **Finance Data Analysis & AI Automation Dashboard** running 100% locally on Python, Flask, Pandas, Scikit-Learn, and Chart.js.

Designed with a professional **light analytics theme with navy blue accents** (`#0F2942`, `#1E3A8A`, `#2563EB`), this platform dynamically converts raw financial datasets into interactive dashboards, statistical anomaly audits, executive reports, and data-backed business insights without relying on fixed column names or external LLM APIs (No ChatGPT/OpenAI).

---

## Key Capabilities & Features

### 1. Universal Financial Data Ingestion & Auto-Cleaning
- **Supported Formats:** CSV, Excel (`.xlsx`, `.xls`).
- **Fuzzy Semantic Schema Discovery:** Automatically identifies monetary fields (Revenue, Expenses, Net Profit, Amounts, Planned Budgets), Categorical segments (Departments, Cost Centers, Product Lines), Dates/Periods, and Payment/Invoice Statuses.
- **Automated Data Normalization:**
  - Cleans currency symbols (`$`, `€`, `£`, `₹`, `¥`), commas, whitespace, and accounting parentheses `(1,250.00)` into valid numbers.
  - Formats European vs standard decimal points.
  - Parses diverse timestamp and date strings into temporal hierarchies (Year, Month, Quarter).
  - Automatically identifies duplicates and missing cells.
- **Data Quality Scorecard:** Real-time health meter (0–100 score), duplicate counter, missing value tracker, and clear diagnostics explaining missing fields if non-financial data is uploaded.

### 2. Dynamic Financial KPI & Visual Dashboard
- **Auto-Calculated Core KPIs:** Total Revenue, Total Expenditures, Net Operating Profit, Profit Margin (%), Transaction Volume, Average Transaction Value.
- **Corporate Budget Variance:** Planned Budget, Actual Spend, Variance ($ and %), and Burn Rate metrics.
- **Interactive Visualizations (Chart.js):**
  - **Revenue & Expense Trajectories:** Dual-axis temporal area/line charts.
  - **Income vs Expense Ratio:** Responsive donut comparison.
  - **Net Profit Evolution:** Period-by-period bar chart with margin indicators.
  - **Cumulative Cash Flow:** Performance trend lines.
  - **Department & Category Breakdown:** Top revenue contributors and cost center allocations.
  - **Budget vs Actual Comparison:** Grouped departmental variance bars.

### 3. Local AI & Statistical Intelligence Module (No ChatGPT / No OpenAI)
- **Machine Learning Anomaly Detection:** Uses `scikit-learn` **Isolation Forest** coupled with robust statistical **Z-Score** modeling ($Z > 2.2\sigma$) to flag anomalous transactions, out-of-cycle spend spikes, and high-variance line items with clear audit explanations.
- **Growth Regression & Momentum Analysis:** Computes Compound Monthly Growth Rates (CMGR %), Ordinary Least Squares slopes, and evaluates whether operating costs are outpacing revenue acceleration (margin compression warning).
- **Pareto 80/20 & Concentration Analysis:** Identifies top revenue engines, largest cost centers, and flags revenue or supplier concentration risks when a single category exceeds 45% of total volume.
- **Data-Backed Actionable Recommendations:** Generates quantified business recommendations (cost rationalization targets, revenue scaling opportunities, and audit checkpoints) based strictly on verified numbers.
- **Natural Language Executive Summary:** Deterministic generation of institutional-grade financial health summaries.

### 4. Automated Multi-Format Report Generation
- **Executive PDF Report (ReportLab):** Formatted multi-section PDF featuring custom corporate navy palette, executive narrative, KPI scorecards, category tables, risk radars, and strategic recommendations.
- **Financial Excel Model (OpenPyXL):** Multi-tab formatted spreadsheet containing:
  - Tab 1: `Executive Summary`
  - Tab 2: `Cleaned Financial Data`
  - Tab 3: `Category Breakdown`
  - Tab 4: `Time Series Trends`
  - Tab 5: `AI Risk & Recommendations`
- **CSV Data Export:** Cleaned, standardized tabular export for downstream analytics.

### 5. Interactive Navigation & Filter Controls
- **Date Range Picker:** Custom start and end date filtering.
- **Aggregation Frequency:** Switch seamlessly between **Monthly**, **Quarterly**, and **Yearly** chart views.
- **Category Filter:** Live dropdown filtering by department, segment, or cost center.
- **Real-Time Search & Pagination:** Live search with instant debounce and pagination controls.

### 6. User Authentication & Registration System (`src/auth_manager.py`)
- **Persistent Local Database:** Powered by embedded SQLite (`data/users.db`) with zero external infrastructure required.
- **Cryptographic Security:** Passwords hashed with salt via PBKDF2:SHA256 (`werkzeug.security`).
- **User Self-Registration:** Allows new users to create personal accounts with username, password, and display name.
- **Pre-Configured Default Demo Account:**
  - **Username:** `admin`
  - **Password:** `admin123`
- **Dynamic Profile Header:** Shows authenticated user avatar initial, username, and secure logout.

---

## 9 Navigation Sections

1. **Overview:** Executive summary, system status, workflow steps, and 1-click sample dataset loaders.
2. **Upload Dataset:** Drag-and-drop file ingestion, data quality meter, schema chip mapping, and missing-info diagnostics.
3. **Financial Dashboard:** Core executive KPI cards, income vs expense donut, revenue & expense trend lines, and profit evolution.
4. **Revenue Analysis:** Deep dive into revenue categories, Pareto contribution, and commercial share distribution.
5. **Expense Analysis:** Cost center breakdown, expenditure distribution, and budget vs actual variance charts.
6. **AI Insights:** Isolation Forest anomaly audit log, growth regression analysis, financial risk matrix, and data-backed recommendations.
7. **Automated Reports:** Live report preview with 1-click PDF, Excel, and CSV download buttons.
8. **Data Management:** Interactive paginated table with live search, column sorting, and CSV export.
9. **Settings:** Currency symbol preference (`$`, `€`, `£`, `₹`, `¥`), anomaly sensitivity slider, and system reset.

---

## Pre-Bundled Sample Datasets

Located in `data/samples/` for immediate 1-click testing:
1. `enterprise_pnl_monthly.csv`: 24-month multi-department P&L with revenue, expenses, budgets, and operating profits.
2. `transactions_ledger.csv`: 350-row granular transaction ledger with signed amounts, income/expense flows, counterparties, and built-in anomalies.
3. `corporate_budget_actuals.xlsx`: Multi-division corporate budget allocation spreadsheet with planned vs actual expenses.

---

## Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Google Chrome, Microsoft Edge, or any modern web browser

### Installation
Open terminal or PowerShell in this directory:
```bash
pip install -r requirements.txt
```

### Starting the Application
You can start the application using any of the following methods:

**Method 1: Using the Windows Batch Launcher**
Double-click `run.bat` or run:
```cmd
run.bat
```

**Method 2: Using PowerShell**
```powershell
.\run.ps1
```

**Method 3: Direct Python Command**
```bash
python app.py
```

Once started, open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## Project Structure

```
FDA AI Project/
├── app.py                     # Main Flask backend application & REST API
├── requirements.txt           # Project dependencies
├── run.bat                    # Windows 1-click batch launcher
├── run.ps1                    # PowerShell launcher
├── README.md                  # Comprehensive documentation
├── src/
│   ├── auth_manager.py        # SQLite user registration, password hashing & verification
│   ├── data_processor.py      # Schema discovery, currency cleaning, data quality scoring
│   ├── financial_kpis.py      # Dynamic KPI calculations, aggregations, Chart.js series
│   ├── ai_engine.py           # Isolation Forest anomaly audit, regression trends, risk matrix
│   └── report_generator.py    # ReportLab PDF & OpenPyXL Excel export engines
├── templates/
│   └── index.html             # Single-page enterprise dashboard HTML
├── static/
│   ├── css/
│   │   └── styles.css         # Enterprise light theme styling (Navy Blue #0F2942)
│   └── js/
│       └── app.js             # Interactive frontend application engine
└── data/
    └── samples/
        ├── enterprise_pnl_monthly.csv     # Sample P&L dataset
        ├── transactions_ledger.csv        # Sample granular transaction ledger
        └── corporate_budget_actuals.xlsx  # Sample Excel budget variance dataset
```
