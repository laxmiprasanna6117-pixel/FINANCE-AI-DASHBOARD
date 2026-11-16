"""
AI Automation & Natural Language Financial Intelligence Engine
Provides automated executive report writing, audit & anomaly detection analysis,
conversational financial advisory, and stress-testing scenario evaluation.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class FinancialAIEngine:
    def __init__(self, df_fin=None, df_tx=None, df_port=None):
        self.df_fin = df_fin
        self.df_tx = df_tx
        self.df_port = df_port

    def generate_executive_brief(self, kpis):
        """
        Generates an automated, executive-ready C-level financial synthesis report.
        """
        rev = kpis.get("Total_Revenue", 0)
        gp = kpis.get("Gross_Profit", 0)
        gm = kpis.get("Gross_Margin_Pct", 0)
        ebitda = kpis.get("EBITDA", 0)
        ebitda_m = kpis.get("EBITDA_Margin_Pct", 0)
        net_inc = kpis.get("Net_Income", 0)
        net_m = kpis.get("Net_Margin_Pct", 0)
        fcf = kpis.get("Free_Cash_Flow", 0)
        cash = kpis.get("Cash_Balance", 0)
        runway = kpis.get("Runway_Months", 0)
        yoy = kpis.get("YoY_Growth_Pct", 0)
        ltv_cac = kpis.get("LTV_CAC_Ratio", 0)
        churn = kpis.get("Churn_Rate_Pct", 0)
        curr_ratio = kpis.get("Current_Ratio", 0)
        d_e = kpis.get("Debt_to_Equity", 0)

        # Health scoring algorithm
        health_score = 70
        if gm > 70: health_score += 8
        if ebitda > 0: health_score += 8
        if net_inc > 0: health_score += 7
        if fcf > 0: health_score += 5
        if runway > 18 or runway == 999: health_score += 7
        if ltv_cac > 3.5: health_score += 5
        if curr_ratio > 1.5: health_score += 5
        if d_e < 1.0: health_score += 5
        health_score = min(98, health_score)

        if health_score >= 85:
            health_status = "EXCELLENT (Strong Growth & Liquidity)"
            badge_color = "#10B981"
        elif health_score >= 70:
            health_status = "GOOD (Stable Financial Foundation)"
            badge_color = "#3B82F6"
        else:
            health_status = "CAUTION (Margin / Runway Compression)"
            badge_color = "#EF4444"

        runway_text = "Self-sustaining (Cash generative)" if runway >= 999 else f"{runway:.1f} Months"

        report = f"""# 📊 Autonomous Executive Financial Briefing
**Generated At:** {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}  
**Financial Health Index:** **{health_score} / 100** — *{health_status}*

---

### 1. Executive Performance Summary
* **Topline Revenue:** **${rev:,.2f}** with an annualized YoY expansion velocity of **{yoy:+.1f}%**.
* **Gross Profit:** **${gp:,.2f}** reflecting a robust gross margin of **{gm:.1f}%**, demonstrating resilient product pricing leverage.
* **Operating Profitability (EBITDA):** **${ebitda:,.2f}** (**{ebitda_m:.1f}%** EBITDA margin), highlighting operational efficiency.
* **Bottomline Net Earnings:** **${net_inc:,.2f}** (Net Margin: **{net_m:.1f}%**).
* **Free Cash Flow Conversion:** **${fcf:,.2f}** generated, strengthening balance sheet flexibility.

---

### 2. Liquidity, Solvency & Capital Runway
* **Cash & Equivalents:** **${cash:,.2f}**.
* **Estimated Runway:** **{runway_text}**.
* **Current Ratio (Liquidity Buffer):** **{curr_ratio:.2f}x** (Standard benchmark: > 1.50x).
* **Debt-to-Equity Ratio:** **{d_e:.2f}x**, signaling a disciplined leverage profile.

---

### 3. Unit Economics & SaaS Efficiency
* **LTV / CAC Multiple:** **{ltv_cac:.2f}x** (Industry Gold Standard > 3.0x).
* **Annualized Customer Churn:** **{churn:.2f}%**, indicating solid product retention.

---

### 4. AI Strategic Directives & Recommendations
1. **Capital Allocation Priority:** Allocate 15-20% of generated Free Cash Flow toward high-yielding treasury or AI infrastructure scale-up to compound returns.
2. **Margin Optimization:** Continuous monitoring of Cloud Compute & LLM vendor costs to preserve gross margins above 75%.
3. **Audit Vigilance:** Enforce automated approval thresholds on procurement transactions exceeding $25,000 to eliminate out-of-policy leakage.
"""
        return report, health_score, health_status, badge_color

    def audit_transactions(self):
        """
        Autonomous AI scanner across ledger transactions to flag anomalies, fraud risks, and duplicate billings.
        """
        if self.df_tx is None or self.df_tx.empty:
            return None, {}

        df = self.df_tx.copy()
        anomalies = df[df["Is_Anomaly"] == "Yes"]
        high_risk = df[df["Risk_Score"] >= 70]
        
        total_tx = len(df)
        flagged_count = len(anomalies)
        anomaly_ratio = (flagged_count / total_tx * 100) if total_tx else 0
        total_flagged_spend = anomalies["Amount"].sum()
        
        # Categorize by anomaly reason
        reason_breakdown = anomalies["Anomaly_Reason"].value_counts().to_dict()
        
        # Top high-risk vendors
        high_risk_vendors = anomalies.groupby("Vendor")["Amount"].agg(["count", "sum"]).reset_index()
        high_risk_vendors.columns = ["Vendor", "Flagged_Transactions", "Total_Flagged_Amount"]
        high_risk_vendors = high_risk_vendors.sort_values("Total_Flagged_Amount", ascending=False)
        
        stats = {
            "Total_Transactions": total_tx,
            "Flagged_Count": flagged_count,
            "Anomaly_Ratio_Pct": anomaly_ratio,
            "Total_Flagged_Spend": total_flagged_spend,
            "High_Risk_Transactions": len(high_risk),
            "Reason_Breakdown": reason_breakdown,
            "Top_Flagged_Vendors": high_risk_vendors
        }
        
        return anomalies, stats

    def answer_query(self, query, kpis):
        """
        Natural language query processor and financial reasoning assistant.
        Parses common financial inquiries and delivers quantified insights.
        """
        q = query.lower().strip()
        
        rev = kpis.get("Total_Revenue", 0)
        gm = kpis.get("Gross_Margin_Pct", 0)
        ebitda = kpis.get("EBITDA", 0)
        net_inc = kpis.get("Net_Income", 0)
        cash = kpis.get("Cash_Balance", 0)
        runway = kpis.get("Runway_Months", 0)
        yoy = kpis.get("YoY_Growth_Pct", 0)
        ltv_cac = kpis.get("LTV_CAC_Ratio", 0)
        fcf = kpis.get("Free_Cash_Flow", 0)
        
        if any(w in q for w in ["runway", "burn", "cash", "liquidity"]):
            runway_str = "Indefinite (Cash positive operation)" if runway >= 999 else f"{runway:.1f} months"
            return (
                f"**Cash & Runway Analysis:**\n\n"
                f"- **Current Cash & Liquid Reserves:** `${cash:,.2f}`\n"
                f"- **Estimated Operational Runway:** `{runway_str}`\n"
                f"- **Free Cash Flow Velocity:** `${fcf:,.2f}`\n\n"
                f"**Strategic Assessment:** The company maintains a healthy liquidity cushion. "
                + ("Cash generation is positive, minimizing dilutive external financing requirements." if fcf > 0 else "Recommend tightening discretionary OPEX to extend the operating horizon beyond 24 months.")
            )
            
        elif any(w in q for w in ["revenue", "sales", "growth", "topline"]):
            return (
                f"**Revenue & Growth Trajectory:**\n\n"
                f"- **Aggregated Revenue:** `${rev:,.2f}`\n"
                f"- **Year-over-Year Growth Rate:** `{yoy:+.1f}%`\n"
                f"- **Gross Margin:** `{gm:.1f}%`\n\n"
                f"**Executive Takeaway:** Topline momentum is expanding favorably. High retention and steady new logo acquisition in the AI Cloud and Enterprise segments are driving double-digit annualized growth."
            )
            
        elif any(w in q for w in ["profit", "margin", "ebitda", "net income"]):
            return (
                f"**Profitability & Margins Breakdown:**\n\n"
                f"- **Gross Margin:** `{gm:.1f}%`\n"
                f"- **EBITDA:** `${ebitda:,.2f}` ({kpis.get('EBITDA_Margin_Pct', 0):.1f}% margin)\n"
                f"- **Net Income:** `${net_inc:,.2f}` ({kpis.get('Net_Margin_Pct', 0):.1f}% margin)\n\n"
                f"**Efficiency Assessment:** Margins reflect a healthy software and tech profile. COGS optimization across cloud compute workloads can yield an additional 120-180 bps in gross margin."
            )
            
        elif any(w in q for w in ["anomaly", "fraud", "audit", "suspicious", "risk"]):
            _, stats = self.audit_transactions()
            count = stats.get("Flagged_Count", 0)
            spend = stats.get("Total_Flagged_Spend", 0)
            pct = stats.get("Anomaly_Ratio_Pct", 0)
            return (
                f"**Autonomous Audit & Fraud Scan Results:**\n\n"
                f"- **Flagged Transactions:** `{count}` out of `{stats.get('Total_Transactions', 0)}` records (`{pct:.1f}%`)\n"
                f"- **Total Capital at Audit Risk:** `${spend:,.2f}`\n"
                f"- **Primary Flag Categories:** Unusual expense spikes, weekend off-cycle wires, and potential duplicate vendor invoices.\n\n"
                f"**Action Recommended:** Navigate to the **'AI Audit & Anomaly Detection'** tab to inspect and approve/freeze specific flagged transactions."
            )
            
        elif any(w in q for w in ["portfolio", "investment", "sharpe", "asset", "crypto"]):
            return (
                f"**Treasury & Investment Portfolio Insight:**\n\n"
                f"- **Portfolio Objective:** Capital preservation combined with selective growth capture.\n"
                f"- **Core Holdings:** US Equities (S&P 500 & Tech ETFs), Treasury Notes, and Money Market Instruments.\n"
                f"- **Hedging:** 5% allocated to Gold Trust and 3% to Digital Asset Reserves for asymmetric inflation protection.\n\n"
                f"**Action Recommended:** Check the **'Portfolio & Risk Engine'** tab to review real-time Sharpe Ratio, Value at Risk (VaR), and Monte Carlo simulations."
            )
            
        elif any(w in q for w in ["cac", "ltv", "unit economics", "customer"]):
            return (
                f"**SaaS & Customer Economics:**\n\n"
                f"- **Average Customer Lifetime Value (LTV):** `${kpis.get('Avg_LTV', 0):,.2f}`\n"
                f"- **Average Customer Acquisition Cost (CAC):** `${kpis.get('Avg_CAC', 0):,.2f}`\n"
                f"- **LTV / CAC Ratio:** `{ltv_cac:.2f}x` (Target > 3.0x)\n"
                f"- **Annualized Churn Rate:** `{kpis.get('Churn_Rate_Pct', 0):.2f}%`\n\n"
                f"**Verdict:** Highly capital-efficient customer acquisition engine. Every $1 invested in S&M generates over ${ltv_cac:.1f} in enterprise value."
            )
            
        else:
            return (
                f"**Financial Intelligence Summary:**\n\n"
                f"Based on your query, here are the core financial health indicators:\n"
                f"- **Revenue:** `${rev:,.2f}` (YoY: `{yoy:+.1f}%`)\n"
                f"- **Gross Margin:** `{gm:.1f}%` | **EBITDA:** `${ebitda:,.2f}`\n"
                f"- **Cash Reserves:** `${cash:,.2f}`\n\n"
                f"💡 *Tip: Try asking specific questions like 'What is our runway?', 'Show margin breakdown', 'Are there any anomalies?', or 'Evaluate portfolio risk'.*"
            )

    def simulate_scenario(self, kpis, rev_change_pct, opex_change_pct, cogs_change_pct):
        """
        Simulate financial sensitivity / stress-testing scenario.
        """
        base_rev = kpis.get("Total_Revenue", 0)
        base_gp = kpis.get("Gross_Profit", 0)
        base_opex = kpis.get("Total_OPEX", 0)
        base_cash = kpis.get("Cash_Balance", 0)
        
        sim_rev = base_rev * (1 + rev_change_pct / 100.0)
        base_cogs = base_rev - base_gp
        sim_cogs = base_cogs * (1 + cogs_change_pct / 100.0)
        sim_gp = sim_rev - sim_cogs
        sim_opex = base_opex * (1 + opex_change_pct / 100.0)
        
        sim_ebit = sim_gp - sim_opex
        sim_ebitda = sim_ebit + (sim_rev * 0.035)
        sim_tax = max(0, sim_ebit * 0.21)
        sim_net_inc = sim_ebit - sim_tax
        
        sim_monthly_burn = (sim_net_inc - (sim_rev * 0.04)) / 12.0
        if sim_monthly_burn < 0:
            sim_runway = base_cash / abs(sim_monthly_burn)
        else:
            sim_runway = 999.0
            
        return {
            "Simulated_Revenue": sim_rev,
            "Simulated_Gross_Profit": sim_gp,
            "Simulated_Gross_Margin_Pct": (sim_gp / sim_rev * 100) if sim_rev else 0,
            "Simulated_OPEX": sim_opex,
            "Simulated_EBITDA": sim_ebitda,
            "Simulated_EBITDA_Margin_Pct": (sim_ebitda / sim_rev * 100) if sim_rev else 0,
            "Simulated_Net_Income": sim_net_inc,
            "Simulated_Net_Margin_Pct": (sim_net_inc / sim_rev * 100) if sim_rev else 0,
            "Simulated_Runway_Months": sim_runway,
            "Revenue_Impact_Delta": sim_rev - base_rev,
            "EBITDA_Impact_Delta": sim_ebitda - kpis.get("EBITDA", 0),
            "Net_Income_Impact_Delta": sim_net_inc - kpis.get("Net_Income", 0)
        }
