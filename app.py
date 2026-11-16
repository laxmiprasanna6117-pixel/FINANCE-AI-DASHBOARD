"""
Finance Data Analysis & AI Automation Dashboard
Enterprise-grade Financial Analytics, Autonomous Auditing, Portfolio Risk Engine, AI Advisor,
User Account Profiles, and Universal Multi-Format CSV Ingestion.
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.data_generator import generate_all, DATA_DIR
from src.data_normalizer import load_and_normalize_csv
from src.auth import (
    load_users,
    register_user,
    authenticate_user,
    add_user_uploaded_file,
    get_user_workspace_dir
)
from src.analytics import calculate_kpis, detect_anomalies, calculate_portfolio_metrics, run_monte_carlo_forecast
from src.ai_engine import FinancialAIEngine
from src.visualizations import (
    make_revenue_ebitda_chart,
    make_segment_breakdown_chart,
    make_opex_breakdown_chart,
    make_portfolio_frontier_chart,
    make_portfolio_allocation_chart,
    make_monte_carlo_fan_chart,
    make_audit_scatter_chart
)
from src.styles import CUSTOM_CSS, metric_card, user_profile_card

# --- Page Setup ---
st.set_page_config(
    page_title="Finance Data Analysis & AI Automation Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Initialize Session State for User Auth & Uploaded Datasets ---
if "current_user" not in st.session_state:
    # Default to initial enterprise CFO account
    users = load_users()
    default_email = "prasad@fda.finance"
    st.session_state["current_user"] = users.get(default_email, list(users.values())[0])

if "active_dataset_name" not in st.session_state:
    st.session_state["active_dataset_name"] = "Default Enterprise Multi-Year Financials"

if "custom_fin_df" not in st.session_state:
    st.session_state["custom_fin_df"] = None

if "custom_tx_df" not in st.session_state:
    st.session_state["custom_tx_df"] = None

if "mapping_info" not in st.session_state:
    st.session_state["mapping_info"] = None

# --- Data Loading with Caching ---
@st.cache_data(show_spinner=False)
def load_default_datasets():
    fin_path = os.path.join(DATA_DIR, "company_financials.csv")
    tx_path = os.path.join(DATA_DIR, "transactions_ledger.csv")
    port_path = os.path.join(DATA_DIR, "portfolio_assets.csv")
    
    if not os.path.exists(fin_path) or not os.path.exists(tx_path) or not os.path.exists(port_path):
        generate_all()
        
    df_fin = pd.read_csv(fin_path)
    df_tx = pd.read_csv(tx_path)
    df_port = pd.read_csv(port_path)
    return df_fin, df_tx, df_port

df_fin_default, df_tx_default, df_port_default = load_default_datasets()

# Decide which dataset is active
if st.session_state["custom_fin_df"] is not None:
    df_fin_active = st.session_state["custom_fin_df"].copy()
    df_tx_active = st.session_state["custom_tx_df"].copy() if st.session_state["custom_tx_df"] is not None else df_tx_default.copy()
else:
    df_fin_active = df_fin_default.copy()
    df_tx_active = df_tx_default.copy()

df_port_active = df_port_default.copy()

# ==============================================================================
# SIDEBAR: USER ACCOUNT & CONTROLS
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bullish.png", width=64)
    st.markdown("### 🏢 **Enterprise Finance Hub**")
    
    # 1. User Profile Card
    current_user = st.session_state["current_user"]
    st.markdown(user_profile_card(current_user), unsafe_allow_html=True)
    
    # User Account Actions: Switch / Register
    with st.expander("👤 Account Profile & Register", expanded=False):
        auth_tab1, auth_tab2 = st.tabs(["Switch Profile", "Register New User"])
        
        with auth_tab1:
            all_users = load_users()
            user_options = {f"{u['name']} ({u['role']})": u['email'] for u in all_users.values()}
            selected_user_label = st.selectbox(
                "Select User Account",
                options=list(user_options.keys()),
                index=0
            )
            if st.button("Switch Account", use_container_width=True):
                target_email = user_options[selected_user_label]
                st.session_state["current_user"] = all_users[target_email]
                st.success(f"Switched to {all_users[target_email]['name']}")
                st.rerun()
                
        with auth_tab2:
            st.markdown("##### Create New User Account")
            new_name = st.text_input("Full Name", placeholder="e.g. Sarah Connor")
            new_email = st.text_input("Corporate Email", placeholder="e.g. sconnor@fda.finance")
            new_org = st.text_input("Organization", placeholder="e.g. FDA BioTech Holdings")
            new_role = st.selectbox(
                "Corporate Role",
                ["Chief Financial Officer (CFO)", "Senior Financial Analyst", "VP of Finance", "Treasury & Risk Director", "Compliance & Audit Lead"]
            )
            new_pass = st.text_input("Password / PIN", type="password", placeholder="At least 4 chars")
            
            if st.button("Register & Log In", use_container_width=True):
                success, result = register_user(new_name, new_email, new_pass, new_org, new_role)
                if success:
                    st.session_state["current_user"] = result
                    st.success(f"Welcome, {result['name']}! Profile created and logged in.")
                    st.rerun()
                else:
                    st.error(result)

    st.markdown("---")
    
    # 2. Universal CSV Ingestion
    st.markdown("#### 📥 **Upload Any Financial CSV**")
    st.caption("Upload any CSV (Sales, Ledger, P&L, Expenses, or Bank statement). Our universal normalizer will auto-map columns.")
    
    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"],
        help="Upload custom corporate financials CSV to override default dataset"
    )
    
    if uploaded_file is not None:
        # Check if already processed to prevent rerun loops
        file_key = f"processed_{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("last_uploaded_key") != file_key:
            with st.spinner("Intelligently normalizing & mapping CSV schema..."):
                norm_fin, norm_tx, mapping_info, success, msg = load_and_normalize_csv(uploaded_file)
                if success and norm_fin is not None:
                    st.session_state["custom_fin_df"] = norm_fin
                    st.session_state["custom_tx_df"] = norm_tx
                    st.session_state["mapping_info"] = mapping_info
                    st.session_state["active_dataset_name"] = uploaded_file.name
                    st.session_state["last_uploaded_key"] = file_key
                    
                    # Save into user's private workspace
                    user_dir = get_user_workspace_dir(current_user["id"])
                    saved_path = os.path.join(user_dir, uploaded_file.name)
                    try:
                        norm_fin.to_csv(saved_path, index=False)
                        add_user_uploaded_file(current_user["email"], uploaded_file.name, saved_path, len(norm_fin), len(norm_fin.columns))
                    except Exception:
                        pass
                        
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # Dataset Toggle (Back to Default)
    if st.session_state["custom_fin_df"] is not None:
        if st.button("⏪ Reset to Default Enterprise Data", use_container_width=True):
            st.session_state["custom_fin_df"] = None
            st.session_state["custom_tx_df"] = None
            st.session_state["mapping_info"] = None
            st.session_state["active_dataset_name"] = "Default Enterprise Multi-Year Financials"
            st.session_state["last_uploaded_key"] = None
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🔍 **Global Filters**")
    
    # Year Filter
    all_years = sorted(df_fin_active["Year"].unique())
    selected_years = st.multiselect("Fiscal Year(s)", options=all_years, default=all_years)
    
    # Segment Filter
    all_segments = sorted(df_fin_active["Segment"].unique())
    selected_segments = st.multiselect("Business Segment / Department", options=all_segments, default=all_segments)
    
    # Region Filter
    all_regions = sorted(df_fin_active["Region"].unique())
    selected_regions = st.multiselect("Geographic Region", options=all_regions, default=all_regions)
    
    st.markdown("---")
    if st.button("🔄 Regenerate Base Data", use_container_width=True):
        st.cache_data.clear()
        generate_all()
        st.session_state["custom_fin_df"] = None
        st.rerun()

# Apply Filters to Active Dataset
filtered_fin = df_fin_active.copy()
if selected_years:
    filtered_fin = filtered_fin[filtered_fin["Year"].isin(selected_years)]
if selected_segments:
    filtered_fin = filtered_fin[filtered_fin["Segment"].isin(selected_segments)]
if selected_regions:
    filtered_fin = filtered_fin[filtered_fin["Region"].isin(selected_regions)]

# If filtering results in empty, fallback to full active
if filtered_fin.empty:
    filtered_fin = df_fin_active.copy()

# Compute KPIs
kpis = calculate_kpis(filtered_fin)
ai_engine = FinancialAIEngine(filtered_fin, df_tx_active, df_port_active)

# --- Header Banner ---
st.markdown(f"""
<div class="header-container">
    <div>
        <h1 class="header-title">Finance Data Analysis & AI Automation Dashboard</h1>
        <div class="header-subtitle">Continuous Real-Time Financial Intelligence, Portfolio Risk Engine & Autonomous Audit Scanner</div>
    </div>
    <div style="text-align: right;">
        <span class="badge-neutral" style="font-size: 0.9rem; padding: 6px 14px;">👤 {current_user['name']} ({current_user['role'].split('(')[-1].replace(')', '')})</span>
        <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 6px;">Org: {current_user['organization']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Active Dataset Notification Banner
is_custom = st.session_state["custom_fin_df"] is not None
active_name = st.session_state["active_dataset_name"]
badge_txt = "CUSTOM USER UPLOAD" if is_custom else "DEFAULT SYSTEM DATASET"
badge_class = "badge-pos" if is_custom else "badge-neutral"

st.markdown(f"""
<div class="dataset-banner">
    <div>
        <strong>Active Dataset:</strong> <code>{active_name}</code> ({len(filtered_fin):,} records active)
        &nbsp;&nbsp;<span class="{badge_class}">{badge_txt}</span>
    </div>
    <div>
        <span>Account: <strong>{current_user['email']}</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

# If custom mapping was performed, show column matching accordion
if st.session_state.get("mapping_info"):
    with st.expander("🔍 View Universal CSV Auto-Column Mapping Breakdown", expanded=False):
        m_info = st.session_state["mapping_info"]
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"- **Raw File Rows:** `{m_info.get('Raw_Rows', 0):,}`")
            st.markdown(f"- **Matched Date Column:** `{m_info.get('Matched_Date')}`")
            st.markdown(f"- **Matched Revenue Column:** `{m_info.get('Matched_Revenue')}`")
            st.markdown(f"- **Matched Costs / Expense:** `{m_info.get('Matched_Costs')}`")
        with col_m2:
            st.markdown(f"- **Matched Profit Column:** `{m_info.get('Matched_Profit')}`")
            st.markdown(f"- **Matched Segment / Category:** `{m_info.get('Matched_Segment')}`")
            st.markdown(f"- **Matched Region / Geo:** `{m_info.get('Matched_Region')}`")
            st.markdown(f"- **Raw Source Columns:** `{', '.join(m_info.get('Raw_Columns', []))}`")

# --- Tabs Navigation ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive Command Center",
    "🤖 AI Financial Intelligence",
    "🛡️ Autonomous Audit & Risk",
    "💼 Portfolio & Risk Engine",
    "🔮 Scenario & Stress Testing",
    "📂 Data Hub & User Workspaces"
])

# ==============================================================================
# TAB 1: EXECUTIVE COMMAND CENTER
# ==============================================================================
with tab1:
    st.markdown("### 📈 Core Financial Health & Performance")
    
    # Top KPI Metrics Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        rev = kpis.get("Total_Revenue", 0)
        yoy = kpis.get("YoY_Growth_Pct", 0)
        badge_type = "pos" if yoy >= 0 else "neg"
        st.markdown(metric_card("Total Revenue", f"${rev:,.0f}", f"vs prior period", f"{yoy:+.1f}% YoY", badge_type), unsafe_allow_html=True)
        
    with c2:
        gm = kpis.get("Gross_Margin_Pct", 0)
        gp = kpis.get("Gross_Profit", 0)
        st.markdown(metric_card("Gross Profit", f"${gp:,.0f}", f"Gross Margin", f"{gm:.1f}%", "pos" if gm > 70 else "neutral"), unsafe_allow_html=True)
        
    with c3:
        ebitda = kpis.get("EBITDA", 0)
        ebitda_m = kpis.get("EBITDA_Margin_Pct", 0)
        st.markdown(metric_card("EBITDA", f"${ebitda:,.0f}", f"Operating Margin", f"{ebitda_m:.1f}%", "pos" if ebitda > 0 else "neg"), unsafe_allow_html=True)
        
    with c4:
        net_inc = kpis.get("Net_Income", 0)
        net_m = kpis.get("Net_Margin_Pct", 0)
        st.markdown(metric_card("Net Income", f"${net_inc:,.0f}", f"Net Profit Margin", f"{net_m:.1f}%", "pos" if net_inc > 0 else "neg"), unsafe_allow_html=True)

    # Top KPI Metrics Row 2
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        cash = kpis.get("Cash_Balance", 0)
        st.markdown(metric_card("Cash & Equivalents", f"${cash:,.0f}", "Liquid Treasury Reserve", "Secure", "neutral"), unsafe_allow_html=True)
        
    with c6:
        runway = kpis.get("Runway_Months", 0)
        runway_txt = "Self-Sustaining" if runway >= 999 else f"{runway:.1f} Mo"
        st.markdown(metric_card("Cash Runway", runway_txt, "Current burn trajectory", "Healthy" if runway > 18 else "Tight", "pos" if runway > 18 else "neg"), unsafe_allow_html=True)
        
    with c7:
        ltv_cac = kpis.get("LTV_CAC_Ratio", 0)
        st.markdown(metric_card("LTV / CAC Ratio", f"{ltv_cac:.2f}x", f"Target Benchmark > 3.0x", "Elite" if ltv_cac > 3.5 else "Standard", "pos"), unsafe_allow_html=True)
        
    with c8:
        curr_ratio = kpis.get("Current_Ratio", 0)
        st.markdown(metric_card("Current Ratio", f"{curr_ratio:.2f}x", "Liquidity Buffer", "Solid" if curr_ratio > 1.5 else "Monitor", "pos" if curr_ratio > 1.5 else "neg"), unsafe_allow_html=True)

    st.markdown("---")
    
    # Charts Section
    col_chart1, col_chart2 = st.columns([3, 2])
    with col_chart1:
        st.markdown("#### 📊 Revenue, EBITDA & Net Income Trajectory")
        chart_rev = make_revenue_ebitda_chart(filtered_fin)
        st.altair_chart(chart_rev, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### 🧩 Revenue by Business Segment")
        chart_seg = make_segment_breakdown_chart(filtered_fin)
        st.altair_chart(chart_seg, use_container_width=True)

    col_chart3, col_chart4 = st.columns([2, 3])
    with col_chart3:
        st.markdown("#### 📉 Cost Structure & OPEX Allocation")
        chart_opex = make_opex_breakdown_chart(filtered_fin)
        st.altair_chart(chart_opex, use_container_width=True)
        
    with col_chart4:
        st.markdown("#### 📋 Financial Summary by Quarter")
        quarterly_summary = filtered_fin.groupby("Quarter").agg({
            "Revenue": "sum",
            "Gross_Profit": "sum",
            "EBITDA": "sum",
            "Net_Income": "sum",
            "Free_Cash_Flow": "sum"
        }).reset_index().tail(8)
        
        for col in ["Revenue", "Gross_Profit", "EBITDA", "Net_Income", "Free_Cash_Flow"]:
            quarterly_summary[col] = quarterly_summary[col].apply(lambda x: f"${x:,.0f}")
            
        st.dataframe(quarterly_summary, use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 2: AI FINANCIAL INTELLIGENCE & ADVISOR
# ==============================================================================
with tab2:
    st.markdown("### 🤖 Autonomous AI Financial Advisory & Synthesis")
    st.caption("Ask complex questions about your balance sheet, P&L, burn rate, or unit economics, and generate one-click executive briefs.")
    
    ai_col1, ai_col2 = st.columns([3, 2])
    
    with ai_col1:
        st.markdown("#### 💬 Ask the AI Financial Analyst")
        
        st.markdown("**Quick Inquiries:**")
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        with chip_col1:
            if st.button("💰 Analyze Cash & Runway", use_container_width=True):
                st.session_state["user_query"] = "How is our cash runway and burn rate looking?"
        with chip_col2:
            if st.button("🚀 Revenue & Growth Review", use_container_width=True):
                st.session_state["user_query"] = "Evaluate our revenue growth and topline momentum"
        with chip_col3:
            if st.button("🛡️ Audit & Anomaly Scan", use_container_width=True):
                st.session_state["user_query"] = "Are there any suspicious anomalies in our transactions?"
                
        user_query = st.text_input(
            "Enter your financial question or strategic analysis request:",
            value=st.session_state.get("user_query", "How is our cash runway and burn rate looking?")
        )
        
        if user_query:
            with st.spinner("AI analyzing financial matrices..."):
                response = ai_engine.answer_query(user_query, kpis)
                st.markdown(f'<div class="ai-bubble">{response}</div>', unsafe_allow_html=True)
                
    with ai_col2:
        st.markdown("#### 📑 Autonomous Executive Brief Generator")
        report_md, health_score, health_status, badge_color = ai_engine.generate_executive_brief(kpis)
        
        st.markdown(f"""
        <div class="fin-card" style="text-align: center; border-color: {badge_color};">
            <div style="font-size: 0.9rem; color: #94A3B8;">COMPREHENSIVE HEALTH INDEX</div>
            <div style="font-size: 2.8rem; font-weight: 800; color: {badge_color}; margin: 8px 0;">{health_score} / 100</div>
            <div style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9;">{health_status}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.download_button(
            label="📥 Download Executive Briefing (Markdown)",
            data=report_md,
            file_name=f"Executive_Financial_Report_{pd.Timestamp.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )
        
    st.markdown("---")
    st.markdown("#### 📄 Executive Briefing Preview")
    with st.expander("Expand full AI briefing document", expanded=True):
        st.markdown(report_md)

# ==============================================================================
# TAB 3: AUTONOMOUS AUDIT & RISK
# ==============================================================================
with tab3:
    st.markdown("### 🛡️ Autonomous Transaction Audit & Anomaly Detection")
    st.caption("Real-time automated auditing across all procurement lines, detecting invoice spikes, off-cycle transfers, and potential duplicate billings.")
    
    anomalies_df, audit_stats = ai_engine.audit_transactions()
    
    aud1, aud2, aud3, aud4 = st.columns(4)
    with aud1:
        st.markdown(metric_card("Total Ledger Records", f"{audit_stats.get('Total_Transactions', 0):,}", "Transactions scanned", "Audited", "neutral"), unsafe_allow_html=True)
    with aud2:
        flg_cnt = audit_stats.get("Flagged_Count", 0)
        pct = audit_stats.get("Anomaly_Ratio_Pct", 0)
        st.markdown(metric_card("Flagged Anomalies", f"{flg_cnt:,}", f"{pct:.1f}% of total volume", "Action Req", "neg"), unsafe_allow_html=True)
    with aud3:
        spend = audit_stats.get("Total_Flagged_Spend", 0)
        st.markdown(metric_card("Capital at Audit Risk", f"${spend:,.0f}", "Requires CFO sign-off", "High Value", "neg"), unsafe_allow_html=True)
    with aud4:
        high_risk = audit_stats.get("High_Risk_Transactions", 0)
        st.markdown(metric_card("Critical Risk Score >= 70", f"{high_risk:,}", "Immediate review", "Priority 1", "neg"), unsafe_allow_html=True)
        
    st.markdown("---")
    
    st.markdown("#### 🔍 Anomaly Scatter Distribution & Risk Score Magnitude")
    audit_chart = make_audit_scatter_chart(df_tx_active)
    st.altair_chart(audit_chart, use_container_width=True)
    
    st.markdown("---")
    
    col_t1, col_t2 = st.columns([3, 2])
    with col_t1:
        st.markdown("#### 🚨 Flagged Transactions Requiring Immediate Audit")
        if anomalies_df is not None and not anomalies_df.empty:
            display_anomalies = anomalies_df[[
                "Transaction_ID", "Date", "Department", "Vendor", "Amount", "Anomaly_Reason", "Risk_Score", "Status"
            ]].copy()
            display_anomalies["Amount"] = display_anomalies["Amount"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_anomalies.head(15), use_container_width=True, hide_index=True)
        else:
            st.info("No anomalies detected.")
            
    with col_t2:
        st.markdown("#### 🏢 Top High-Risk Vendors")
        top_vendors = audit_stats.get("Top_Flagged_Vendors")
        if top_vendors is not None and not top_vendors.empty:
            display_vendors = top_vendors.copy()
            display_vendors["Total_Flagged_Amount"] = display_vendors["Total_Flagged_Amount"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_vendors.head(10), use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 4: PORTFOLIO & RISK ENGINE
# ==============================================================================
with tab4:
    st.markdown("### 💼 Corporate Treasury Portfolio & Quantitative Risk Modeling")
    st.caption("Modern Portfolio Theory analytics, Sharpe Ratio optimization, Value at Risk (VaR), and Stochastic Monte Carlo Simulations.")
    
    port_metrics = calculate_portfolio_metrics(df_port_active)
    
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        aum = port_metrics["Total_Portfolio_Value_M"]
        st.markdown(metric_card("Total Treasury AUM", f"${aum:.1f}M", "Active Asset Allocation", "7 Assets", "neutral"), unsafe_allow_html=True)
    with p2:
        exp_ret = port_metrics["Weighted_Return_Pct"]
        st.markdown(metric_card("Expected Annual Return", f"{exp_ret:.2f}%", "Weighted Expected Yield", "Equities + Debt", "pos"), unsafe_allow_html=True)
    with p3:
        sharpe = port_metrics["Sharpe_Ratio"]
        st.markdown(metric_card("Sharpe Ratio", f"{sharpe:.2f}", "Risk-adjusted return", "Excellent" if sharpe > 1.0 else "Fair", "pos" if sharpe > 1.0 else "neutral"), unsafe_allow_html=True)
    with p4:
        var_95 = port_metrics["VaR_95_Value_M"]
        st.markdown(metric_card("Value at Risk (95% 1-Yr)", f"${var_95:.2f}M", f"{port_metrics['VaR_95_Pct']:.1f}% potential drawdown", "Conservative", "neutral"), unsafe_allow_html=True)
        
    st.markdown("---")
    
    p_col1, p_col2 = st.columns([3, 2])
    with p_col1:
        st.markdown("#### 🎯 Risk vs Return Efficient Frontier")
        st.altair_chart(make_portfolio_frontier_chart(df_port_active), use_container_width=True)
    with p_col2:
        st.markdown("#### ⚖️ Target Asset Allocation Breakdown")
        st.altair_chart(make_portfolio_allocation_chart(df_port_active), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🎲 Stochastic Monte Carlo Financial Forecast Engine")
    st.caption("Simulate hundreds of stochastic geometric brownian motion paths to stress-test future treasury balances or revenue targets.")
    
    mc_c1, mc_c2, mc_c3, mc_c4 = st.columns(4)
    with mc_c1:
        sim_months = st.slider("Forecast Horizon (Months)", min_value=6, max_value=36, value=24, step=6)
    with mc_c2:
        sim_growth = st.slider("Monthly Expected Growth (%)", min_value=-2.0, max_value=5.0, value=1.8, step=0.1) / 100.0
    with mc_c3:
        sim_vol = st.slider("Monthly Volatility (%)", min_value=1.0, max_value=15.0, value=4.5, step=0.5) / 100.0
    with mc_c4:
        n_sims = st.selectbox("Number of Simulated Paths", options=[250, 500, 1000], index=1)
        
    latest_monthly_rev = filtered_fin.groupby("Date")["Revenue"].sum().iloc[-1]
    mc_summary, mc_samples = run_monte_carlo_forecast(
        initial_val=latest_monthly_rev,
        monthly_growth_mean=sim_growth,
        monthly_vol=sim_vol,
        n_months=sim_months,
        n_simulations=n_sims
    )
    
    st.altair_chart(make_monte_carlo_fan_chart(mc_summary, mc_samples), use_container_width=True)
    
    st.markdown("##### 📊 Percentile Outcomes at Horizon End")
    final_row = mc_summary.iloc[-1]
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("P10 (Bearish Case)", f"${final_row['P10_Bearish']:,.0f}")
    f2.metric("P25 (Conservative)", f"${final_row['P25_Conservative']:,.0f}")
    f3.metric("P50 (Median Expected)", f"${final_row['P50_Median']:,.0f}")
    f4.metric("P75 (Optimistic)", f"${final_row['P75_Optimistic']:,.0f}")
    f5.metric("P90 (Bullish Case)", f"${final_row['P90_Bullish']:,.0f}")

# ==============================================================================
# TAB 5: SCENARIO & STRESS TESTING
# ==============================================================================
with tab5:
    st.markdown("### 🔮 Dynamic What-If Financial Stress Testing")
    st.caption("Real-time sensitivity modeling: adjust macroeconomic and operational levers to gauge immediate impact on EBITDA and cash runway.")
    
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        rev_shock = st.slider("Topline Revenue Shift (%)", min_value=-30, max_value=30, value=0, step=5, help="Simulate demand drop or surge")
    with s_col2:
        opex_adj = st.slider("OPEX Optimization / Change (%)", min_value=-30, max_value=30, value=0, step=5, help="Simulate headcount or tooling cuts")
    with s_col3:
        cogs_shift = st.slider("COGS / Inflation Shift (%)", min_value=-15, max_value=25, value=0, step=5, help="Simulate cloud compute or supplier cost inflation")
        
    sim_result = ai_engine.simulate_scenario(kpis, rev_shock, opex_adj, cogs_shift)
    
    st.markdown("---")
    
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(metric_card(
            "Simulated Revenue",
            f"${sim_result['Simulated_Revenue']:,.0f}",
            "Impact Delta",
            f"{sim_result['Revenue_Impact_Delta']:+,.0f}",
            "pos" if sim_result['Revenue_Impact_Delta'] >= 0 else "neg"
        ), unsafe_allow_html=True)
    with sc2:
        st.markdown(metric_card(
            "Simulated Gross Margin",
            f"{sim_result['Simulated_Gross_Margin_Pct']:.1f}%",
            f"${sim_result['Simulated_Gross_Profit']:,.0f}",
            "Gross Profit",
            "pos" if sim_result['Simulated_Gross_Margin_Pct'] > 70 else "neutral"
        ), unsafe_allow_html=True)
    with sc3:
        st.markdown(metric_card(
            "Simulated EBITDA",
            f"${sim_result['Simulated_EBITDA']:,.0f}",
            "EBITDA Delta",
            f"{sim_result['EBITDA_Impact_Delta']:+,.0f}",
            "pos" if sim_result['EBITDA_Impact_Delta'] >= 0 else "neg"
        ), unsafe_allow_html=True)
    with sc4:
        sim_runway = sim_result['Simulated_Runway_Months']
        runway_lbl = "Self-Sustaining" if sim_runway >= 999 else f"{sim_runway:.1f} Mo"
        st.markdown(metric_card(
            "Projected Runway",
            runway_lbl,
            "Post-Shock Runway",
            "Safe" if sim_runway > 18 else "Critical",
            "pos" if sim_runway > 18 else "neg"
        ), unsafe_allow_html=True)

    st.markdown("#### 📊 Base Case vs Stress-Tested Scenario Comparison")
    comp_df = pd.DataFrame({
        "Financial Metric": ["Total Revenue", "Gross Profit", "Total OPEX", "EBITDA", "Net Income"],
        "Base Case": [
            f"${kpis.get('Total_Revenue', 0):,.2f}",
            f"${kpis.get('Gross_Profit', 0):,.2f}",
            f"${kpis.get('Total_OPEX', 0):,.2f}",
            f"${kpis.get('EBITDA', 0):,.2f}",
            f"${kpis.get('Net_Income', 0):,.2f}"
        ],
        "Stress-Tested Case": [
            f"${sim_result['Simulated_Revenue']:,.2f}",
            f"${sim_result['Simulated_Gross_Profit']:,.2f}",
            f"${sim_result['Simulated_OPEX']:,.2f}",
            f"${sim_result['Simulated_EBITDA']:,.2f}",
            f"${sim_result['Simulated_Net_Income']:,.2f}"
        ],
        "Variance ($)": [
            f"${sim_result['Revenue_Impact_Delta']:+,.2f}",
            f"${sim_result['Simulated_Gross_Profit'] - kpis.get('Gross_Profit', 0):+,.2f}",
            f"${sim_result['Simulated_OPEX'] - kpis.get('Total_OPEX', 0):+,.2f}",
            f"${sim_result['EBITDA_Impact_Delta']:+,.2f}",
            f"${sim_result['Net_Income_Impact_Delta']:+,.2f}"
        ]
    })
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 6: DATA HUB & USER WORKSPACES
# ==============================================================================
with tab6:
    st.markdown("### 📂 Data Hub, User Workspaces & Custom Export")
    st.caption("Manage your user-specific uploads, inspect raw data tables, or export transformed datasets.")
    
    st.markdown(f"#### 👤 **User Workspace:** `{current_user['name']}` ({current_user['email']})")
    user_uploads = current_user.get("uploaded_files", [])
    if user_uploads:
        st.markdown(f"**Your Uploaded Files History ({len(user_uploads)} files):**")
        up_df = pd.DataFrame(user_uploads)
        st.dataframe(up_df, use_container_width=True, hide_index=True)
    else:
        st.info("No custom files saved in this user account yet. Upload a CSV using the sidebar to populate your workspace.")
        
    st.markdown("---")
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Active Financial Dataset", "Active Transactions Ledger", "Portfolio Assets"])
    
    with sub_tab1:
        st.markdown(f"**Total Records Active:** {len(filtered_fin):,} rows")
        st.dataframe(filtered_fin, use_container_width=True)
        csv_fin = filtered_fin.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Active Financials as CSV",
            data=csv_fin,
            file_name=f"active_financials_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    with sub_tab2:
        st.markdown(f"**Total Transactions Active:** {len(df_tx_active):,} rows")
        st.dataframe(df_tx_active, use_container_width=True)
        csv_tx = df_tx_active.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Ledger as CSV",
            data=csv_tx,
            file_name=f"active_ledger_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    with sub_tab3:
        st.markdown(f"**Total Portfolio Assets:** {len(df_port_active):,} assets")
        st.dataframe(df_port_active, use_container_width=True)
        csv_port = df_port_active.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Portfolio Assets as CSV",
            data=csv_port,
            file_name="portfolio_assets_export.csv",
            mime="text/csv"
        )

st.markdown("---")
st.caption(f"© 2026 Enterprise Finance AI Automation Platform | Logged in as {current_user['name']} ({current_user['role']})")
