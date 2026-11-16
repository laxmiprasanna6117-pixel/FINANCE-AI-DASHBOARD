"""
Data Generator for Finance Data Analysis & AI Automation Dashboard.
Generates realistic multi-year corporate financial records, ledger transactions, and investment portfolios.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def generate_financials_data(seed=42):
    np.random.seed(seed)
    months = pd.date_range(start="2023-01-01", end="2026-10-31", freq="MS")
    segments = ["Enterprise SaaS", "AI Cloud Services", "FinTech Solutions"]
    regions = ["North America", "Europe", "Asia-Pacific"]
    
    records = []
    
    # Base starting metrics per segment
    base_rev = {"Enterprise SaaS": 1200000, "AI Cloud Services": 800000, "FinTech Solutions": 600000}
    growth_rates = {"Enterprise SaaS": 0.022, "AI Cloud Services": 0.045, "FinTech Solutions": 0.018}
    gross_margin_target = {"Enterprise SaaS": 0.78, "AI Cloud Services": 0.68, "FinTech Solutions": 0.82}
    
    cash_balance = 35000000.0  # Starting cash $35M
    
    for i, date_val in enumerate(months):
        year = date_val.year
        quarter = f"Q{(date_val.month - 1) // 3 + 1} {year}"
        
        for seg in segments:
            for reg in regions:
                reg_weight = {"North America": 0.50, "Europe": 0.30, "Asia-Pacific": 0.20}[reg]
                
                # Dynamic growth curve + seasonality
                month_idx = date_val.month
                seasonality = 1.0 + (0.12 if month_idx in [11, 12] else (-0.05 if month_idx in [1, 7] else 0.02))
                noise = np.random.normal(1.0, 0.04)
                
                monthly_rev = base_rev[seg] * ((1 + growth_rates[seg]) ** i) * reg_weight * seasonality * noise
                gm_pct = np.clip(gross_margin_target[seg] + np.random.normal(0, 0.015), 0.55, 0.90)
                cogs = monthly_rev * (1 - gm_pct)
                gross_profit = monthly_rev - cogs
                
                # OPEX allocations
                rnd_exp = monthly_rev * (0.24 + np.random.normal(0, 0.01))
                sm_exp = monthly_rev * (0.28 + np.random.normal(0, 0.015))
                ga_exp = monthly_rev * (0.12 + np.random.normal(0, 0.008))
                total_opex = rnd_exp + sm_exp + ga_exp
                
                ebit = gross_profit - total_opex
                ebitda = ebit + (monthly_rev * 0.035)  # depreciation & amortization proxy
                interest_exp = 15000.0 * reg_weight
                tax_rate = 0.21
                ebt = ebit - interest_exp
                tax = max(0, ebt * tax_rate)
                net_income = ebt - tax
                
                # Cash Flow elements
                capex = monthly_rev * 0.04 + np.random.uniform(5000, 20000)
                change_working_capital = np.random.normal(0, monthly_rev * 0.01)
                operating_cf = net_income + (monthly_rev * 0.035) - change_working_capital
                free_cf = operating_cf - capex
                
                # Balance Sheet elements proxy
                cash_balance += free_cf * 0.15 # incremental accumulation
                current_assets = monthly_rev * 3.8 + cash_balance * (reg_weight * 0.3)
                total_assets = current_assets * 2.2
                current_liabilities = monthly_rev * 1.4
                total_debt = monthly_rev * 2.1
                total_equity = total_assets - total_debt - current_liabilities
                
                # SaaS / Unit Economics
                headcount = int(120 * ((1 + 0.012) ** i) * reg_weight) + 5
                customer_count = int(180 * ((1 + growth_rates[seg] * 0.8) ** i) * reg_weight) + 10
                cac = 4200.0 + np.random.normal(0, 250)
                ltv = cac * (4.2 + (0.5 if seg == "AI Cloud Services" else 0.1))
                churn_rate = max(0.008, 0.024 - (i * 0.0002) + np.random.normal(0, 0.002))
                
                records.append({
                    "Date": date_val.strftime("%Y-%m-%d"),
                    "Year": year,
                    "Quarter": quarter,
                    "Segment": seg,
                    "Region": reg,
                    "Revenue": round(monthly_rev, 2),
                    "COGS": round(cogs, 2),
                    "Gross_Profit": round(gross_profit, 2),
                    "Gross_Margin_Pct": round(gm_pct * 100, 2),
                    "RD_Expense": round(rnd_exp, 2),
                    "SM_Expense": round(sm_exp, 2),
                    "GA_Expense": round(ga_exp, 2),
                    "Total_OPEX": round(total_opex, 2),
                    "Operating_Income": round(ebit, 2),
                    "EBITDA": round(ebitda, 2),
                    "EBITDA_Margin_Pct": round((ebitda / monthly_rev) * 100, 2),
                    "Net_Income": round(net_income, 2),
                    "Net_Margin_Pct": round((net_income / monthly_rev) * 100, 2),
                    "Operating_Cash_Flow": round(operating_cf, 2),
                    "CapEx": round(capex, 2),
                    "Free_Cash_Flow": round(free_cf, 2),
                    "Cash_Equivalents": round(cash_balance * reg_weight, 2),
                    "Current_Assets": round(current_assets, 2),
                    "Total_Assets": round(total_assets, 2),
                    "Current_Liabilities": round(current_liabilities, 2),
                    "Total_Debt": round(total_debt, 2),
                    "Total_Equity": round(total_equity, 2),
                    "Headcount": headcount,
                    "Customer_Count": customer_count,
                    "CAC": round(cac, 2),
                    "LTV": round(ltv, 2),
                    "LTV_CAC_Ratio": round(ltv / cac, 2),
                    "Churn_Rate_Pct": round(churn_rate * 100, 2)
                })
                
    df = pd.DataFrame(records)
    path = os.path.join(DATA_DIR, "company_financials.csv")
    df.to_csv(path, index=False)
    return df

def generate_transactions_data(seed=101):
    np.random.seed(seed)
    departments = ["Engineering", "Product & AI", "Marketing & Growth", "Sales", "Legal & Compliance", "Operations & HR"]
    vendors_by_dept = {
        "Engineering": ["AWS Cloud Infrastructure", "Snowflake Data Warehouse", "GitHub Enterprise", "Datadog Monitoring", "MongoDB Atlas"],
        "Product & AI": ["OpenAI API Services", "Anthropic Claude AI", "Scale AI Labeling", "Pinecone Vector DB", "Weights & Biases"],
        "Marketing & Growth": ["Google Ads", "LinkedIn Marketing", "HubSpot CRM", "Meta Advertising", "Gartner Market Intelligence"],
        "Sales": ["Salesforce Enterprise", "ZoomInfo Tech", "Gong.io Analytics", "DocuSign", "Highspot Enablement"],
        "Legal & Compliance": ["Deloitte Advisory", "Wilson Sonsini Law", "Vanta Compliance SOC2", "Ernst & Young Audit", "PwC Tax"],
        "Operations & HR": ["Workday HRMS", "WeWork Global Offices", "Deel Global Payroll", "Slack Technologies", "Brex Corporate Cards"]
    }
    
    categories = {
        "Engineering": "Cloud Compute & Infra",
        "Product & AI": "AI Models & APIs",
        "Marketing & Growth": "Digital Ads & Acquisition",
        "Sales": "Sales Enablement & CRM",
        "Legal & Compliance": "Legal, Audit & Compliance",
        "Operations & HR": "Workplace & People Ops"
    }
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 10, 31)
    delta_days = (end_date - start_date).days
    
    transactions = []
    
    for i in range(1, 1201):
        dept = np.random.choice(departments)
        vendor = np.random.choice(vendors_by_dept[dept])
        cat = categories[dept]
        
        rand_days = np.random.randint(0, delta_days)
        tx_date = start_date + timedelta(days=rand_days)
        
        # Base amounts depending on dept
        if dept in ["Engineering", "Product & AI"]:
            base_amt = np.random.exponential(scale=18500) + 1200
        elif dept == "Marketing & Growth":
            base_amt = np.random.exponential(scale=14000) + 800
        elif dept == "Legal & Compliance":
            base_amt = np.random.exponential(scale=25000) + 5000
        else:
            base_amt = np.random.exponential(scale=7500) + 400
            
        amount = round(base_amt, 2)
        payment_method = np.random.choice(["Corporate Wire", "ACH Transfer", "Corporate Card", "Direct Debit"], p=[0.45, 0.35, 0.15, 0.05])
        
        # Inject anomalies intentionally for AI fraud / audit detector
        is_anomaly = False
        anomaly_reason = "Normal"
        risk_score = np.random.randint(5, 30)
        
        # 3% chance of high-value spike
        if np.random.rand() < 0.035:
            amount = round(amount * np.random.uniform(4.5, 9.0), 2)
            is_anomaly = True
            anomaly_reason = "Unusual Expense Magnitude Spike"
            risk_score = np.random.randint(75, 98)
        # 1.5% chance of weekend / unverified off-cycle billing
        elif tx_date.weekday() >= 5 and amount > 20000:
            is_anomaly = True
            anomaly_reason = "Off-cycle Weekend High Value Transfer"
            risk_score = np.random.randint(65, 88)
        # 1.5% duplicate invoice risk
        elif np.random.rand() < 0.015:
            is_anomaly = True
            anomaly_reason = "Potential Duplicate Billing Pattern"
            risk_score = np.random.randint(60, 85)
            
        status = "Flagged for Audit" if is_anomaly else np.random.choice(["Approved", "Settled", "Pending Review"], p=[0.75, 0.20, 0.05])
        
        transactions.append({
            "Transaction_ID": f"TXN-{year_prefix(tx_date.year)}-{i:05d}",
            "Date": tx_date.strftime("%Y-%m-%d"),
            "Department": dept,
            "Category": cat,
            "Vendor": vendor,
            "Amount": amount,
            "Payment_Method": payment_method,
            "Status": status,
            "Is_Anomaly": "Yes" if is_anomaly else "No",
            "Anomaly_Reason": anomaly_reason,
            "Risk_Score": risk_score
        })
        
    df = pd.DataFrame(transactions).sort_values("Date", ascending=False)
    path = os.path.join(DATA_DIR, "transactions_ledger.csv")
    df.to_csv(path, index=False)
    return df

def year_prefix(year):
    return str(year)[-2:]

def generate_portfolio_data():
    portfolio = [
        {"Asset_Name": "US Large-Cap Equity Index (S&P 500)", "Ticker": "SPY", "Asset_Class": "Public Equities", "Allocation_Pct": 28.0, "Expected_Annual_Return_Pct": 11.5, "Annual_Volatility_Pct": 16.2, "Beta": 1.00, "Current_Value_M": 14.0},
        {"Asset_Name": "US Tech Growth Leaders ETF", "Ticker": "QQQ", "Asset_Class": "Public Equities", "Allocation_Pct": 22.0, "Expected_Annual_Return_Pct": 16.8, "Annual_Volatility_Pct": 21.5, "Beta": 1.25, "Current_Value_M": 11.0},
        {"Asset_Name": "US Treasury 7-10 Year Notes", "Ticker": "IEF", "Asset_Class": "Government Bonds", "Allocation_Pct": 18.0, "Expected_Annual_Return_Pct": 4.6, "Annual_Volatility_Pct": 6.8, "Beta": 0.08, "Current_Value_M": 9.0},
        {"Asset_Name": "Investment Grade Corporate Debt", "Ticker": "LQD", "Asset_Class": "Fixed Income", "Allocation_Pct": 14.0, "Expected_Annual_Return_Pct": 5.9, "Annual_Volatility_Pct": 8.4, "Beta": 0.22, "Current_Value_M": 7.0},
        {"Asset_Name": "Short-Term Treasury Money Market", "Ticker": "BIL", "Asset_Class": "Cash Equivalents", "Allocation_Pct": 10.0, "Expected_Annual_Return_Pct": 4.2, "Annual_Volatility_Pct": 1.1, "Beta": 0.01, "Current_Value_M": 5.0},
        {"Asset_Name": "Gold & Precious Metals Trust", "Ticker": "GLD", "Asset_Class": "Commodities & Hedge", "Allocation_Pct": 5.0, "Expected_Annual_Return_Pct": 8.2, "Annual_Volatility_Pct": 14.0, "Beta": 0.12, "Current_Value_M": 2.5},
        {"Asset_Name": "Digital Asset Treasury Reserve", "Ticker": "BTC", "Asset_Class": "Alternative Assets", "Allocation_Pct": 3.0, "Expected_Annual_Return_Pct": 28.0, "Annual_Volatility_Pct": 58.0, "Beta": 1.85, "Current_Value_M": 1.5}
    ]
    df = pd.DataFrame(portfolio)
    path = os.path.join(DATA_DIR, "portfolio_assets.csv")
    df.to_csv(path, index=False)
    return df

def generate_all():
    ensure_data_dir()
    print("Generating enterprise financials dataset...")
    df_fin = generate_financials_data()
    print(f"Company financials generated: {len(df_fin)} rows.")
    
    print("Generating transactions ledger dataset...")
    df_tx = generate_transactions_data()
    print(f"Transactions ledger generated: {len(df_tx)} rows.")
    
    print("Generating investment portfolio dataset...")
    df_port = generate_portfolio_data()
    print(f"Portfolio assets generated: {len(df_port)} assets.")
    print("All datasets generated successfully!")

if __name__ == "__main__":
    generate_all()
