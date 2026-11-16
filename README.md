# 📈 Finance Data Analysis & AI Automation Dashboard

An enterprise-grade, high-performance Financial Intelligence, Continuous Auditing, and Autonomous Strategic Advisory platform built with Python, Streamlit, Pandas, and Altair.

---

## 🌟 Key Capabilities & Modules

### 1. 📊 Executive KPI Command Center
- **Core P&L Metrics:** Instant tracking of Total Revenue, Gross Profit, Gross Margin %, EBITDA, Net Income, and Operating Cash Flow.
- **Liquidity & Solvency Ratios:** Real-time Current Ratio, Debt-to-Equity, Liquid Treasury Balances, and Net Cash Runway calculation.
- **SaaS & Unit Economics:** Customer Acquisition Cost (CAC), Lifetime Value (LTV), LTV:CAC Multiples, and Churn Velocity.
- **Visual Trends:** Interactive dual-axis growth curves, Business Segment area breakdowns, and OPEX component allocations.

### 2. 🤖 AI Financial Advisor & Strategic Synthesis
- **Autonomous C-Level Briefing Generator:** One-click generation of institutional-grade executive reports with a composite Financial Health Index (0–100 score).
- **Conversational Financial Query Engine:** Natural-language analysis answering queries on burn rate, runway, growth trajectory, unit economics, and margin optimization.
- **One-Click Export:** Download executive briefings directly in Markdown or PDF-ready formats.

### 3. 🛡️ Autonomous Audit & Anomaly Detection
- **Continuous Procurement Scanner:** Automated auditing across general ledger transactions flagging invoice spikes, off-cycle transfers, and potential duplicate billings.
- **Risk Scoring Engine:** Categorizes transactions by risk score (0–100) with anomaly reason tagging.
- **Capital at Risk Metrics:** Real-time visibility into total capital requiring CFO authorization.

### 4. 💼 Corporate Treasury Portfolio & Quantitative Risk Modeling
- **Modern Portfolio Theory Analytics:** Weighted Expected Return, Portfolio Volatility, Sharpe Ratio, Sortino Ratio, and Beta.
- **Value at Risk (VaR):** Parametric 95% and 99% annual VaR projections.
- **Stochastic Monte Carlo Simulation Engine:** Geometric Brownian Motion simulation projecting 100 to 1,000 stochastic paths with confidence percentile ribbons (P10, P25, P50 Median, P75, P90).

### 5. 🔮 Dynamic What-If Stress Testing & Scenario Simulator
- **Interactive Financial Shock Sliders:** Test revenue contractions/expansions (-30% to +30%), OPEX adjustments (-30% to +30%), and COGS/supplier inflation shifts.
- **Instant Impact Delta:** Computes simulated EBITDA, net profit margins, and resulting cash runway changes in real time.

### 6. 📂 Data Ingestion & Export Hub
- **Custom CSV Drag-and-Drop:** Ingest custom enterprise financials to dynamically replace baseline datasets.
- **One-Click Data Exports:** Export filtered financials, audited transaction logs, and portfolio holdings directly to CSV.

---

## 🏗️ Directory Architecture

```
FDA AI Project/
├── data/
│   ├── company_financials.csv    # Multi-year segmented financial dataset (2023-2026)
│   ├── transactions_ledger.csv   # General ledger records with anomaly & risk tags
│   └── portfolio_assets.csv      # Corporate treasury multi-asset allocation table
├── src/
│   ├── __init__.py
│   ├── data_generator.py         # Realistic enterprise financial data generator
│   ├── analytics.py              # Financial KPIs, anomaly detection, Sharpe ratio, Monte Carlo
│   ├── ai_engine.py              # Financial conversational engine, audit scanner, scenario modeling
│   ├── visualizations.py         # Interactive Altair visualization components
│   └── styles.py                 # FinTech dark theme styling & metric card components
├── tests/
│   └── test_engine.py            # Unit test suite verifying quantitative algorithms
├── app.py                        # Main Streamlit Dashboard Application
├── run.bat                       # 1-click Windows launcher
├── run.ps1                       # 1-click PowerShell launcher
├── requirements.txt              # Project dependencies
└── README.md                     # Comprehensive documentation
```

---

## 🚀 How to Run the Dashboard

### Option A: One-Click Launcher (Windows)
Double-click `run.bat` or run:
```bat
.\run.bat
```

### Option B: PowerShell
```powershell
.\run.ps1
```

### Option C: Manual Command Line
```bash
python -m streamlit run app.py
```
Open your browser and navigate to: **`http://localhost:8501`**

---

## 🧪 Running Unit Tests

To run the automated test suite verifying financial models, Sharpe ratio, Monte Carlo paths, and the AI engine:
```bash
python -m unittest tests/test_engine.py
```

---

## 🛠️ Customization & Extensibility
- **Custom Financials:** Place your custom financials in `data/company_financials.csv` or upload them directly via the sidebar in the UI.
- **Adding New Portfolio Assets:** Modify or append new rows to `data/portfolio_assets.csv`.
- **Threshold Adjustments:** Modify anomaly detection Z-score thresholds in `src/analytics.py` or risk scoring parameters in `src/ai_engine.py`.
