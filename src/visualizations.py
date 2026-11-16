"""
Interactive Visualizations Engine using Altair & Streamlit.
Provides financial charts: revenue trends, margin breakdowns, asset allocations,
Monte Carlo fan charts, risk frontiers, and transaction audit plots.
"""

import altair as alt
import pandas as pd
import numpy as np

# Apply clean modern FinTech theme styling to Altair charts
def get_chart_theme():
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "axis": {
                "labelColor": "#94A3B8",
                "titleColor": "#E2E8F0",
                "gridColor": "#334155",
                "domainColor": "#475569",
                "labelFontSize": 11,
                "titleFontSize": 12
            },
            "legend": {
                "labelColor": "#E2E8F0",
                "titleColor": "#94A3B8",
                "labelFontSize": 11,
                "titleFontSize": 12
            }
        }
    }

def make_revenue_ebitda_chart(df):
    """
    Monthly Revenue and EBITDA growth trend chart.
    """
    monthly = df.groupby("Date")[["Revenue", "EBITDA", "Net_Income"]].sum().reset_index()
    monthly["Date"] = pd.to_datetime(monthly["Date"])
    
    melted = monthly.melt(id_vars=["Date"], value_vars=["Revenue", "EBITDA", "Net_Income"],
                          var_name="Metric", value_name="Amount")
    
    color_scale = alt.Scale(
        domain=["Revenue", "EBITDA", "Net_Income"],
        range=["#3B82F6", "#10B981", "#8B5CF6"]
    )
    
    chart = alt.Chart(melted).mark_line(point=True, strokeWidth=2.5).encode(
        x=alt.X("Date:T", title="Timeline", axis=alt.Axis(format="%b %Y")),
        y=alt.Y("Amount:Q", title="Amount ($)", axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Metric:N", scale=color_scale, legend=alt.Legend(title="Financial Metric")),
        tooltip=[
            alt.Tooltip("Date:T", format="%B %Y"),
            alt.Tooltip("Metric:N"),
            alt.Tooltip("Amount:Q", format="$,.2f")
        ]
    ).properties(height=360).interactive()
    
    return chart

def make_segment_breakdown_chart(df):
    """
    Revenue contribution broken down by business segment over time.
    """
    seg_df = df.groupby(["Date", "Segment"])["Revenue"].sum().reset_index()
    seg_df["Date"] = pd.to_datetime(seg_df["Date"])
    
    chart = alt.Chart(seg_df).mark_area(opacity=0.85).encode(
        x=alt.X("Date:T", title="Timeline", axis=alt.Axis(format="%b %Y")),
        y=alt.Y("Revenue:Q", stack="zero", title="Segment Revenue ($)", axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Segment:N", scale=alt.Scale(scheme="tableau10"), legend=alt.Legend(title="Business Segment")),
        tooltip=[
            alt.Tooltip("Date:T", format="%B %Y"),
            alt.Tooltip("Segment:N"),
            alt.Tooltip("Revenue:Q", format="$,.2f")
        ]
    ).properties(height=340).interactive()
    
    return chart

def make_opex_breakdown_chart(df):
    """
    Breakdown of OPEX components: R&D, S&M, and G&A.
    """
    latest_quarter = df["Quarter"].iloc[-1] if not df.empty else ""
    recent_df = df[df["Quarter"] == latest_quarter] if latest_quarter else df
    
    opex_data = pd.DataFrame({
        "Category": ["Research & Development (R&D)", "Sales & Marketing (S&M)", "General & Administrative (G&A)", "Cost of Goods Sold (COGS)"],
        "Amount": [
            recent_df["RD_Expense"].sum(),
            recent_df["SM_Expense"].sum(),
            recent_df["GA_Expense"].sum(),
            recent_df["COGS"].sum()
        ]
    })
    
    chart = alt.Chart(opex_data).mark_bar(cornerRadius=6).encode(
        x=alt.X("Amount:Q", title="Spend ($)", axis=alt.Axis(format="$,.0f")),
        y=alt.Y("Category:N", sort="-x", title="Cost Center"),
        color=alt.Color("Category:N", scale=alt.Scale(scheme="tealblues"), legend=None),
        tooltip=[alt.Tooltip("Category:N"), alt.Tooltip("Amount:Q", format="$,.2f")]
    ).properties(height=260)
    
    return chart

def make_portfolio_frontier_chart(df_port):
    """
    Risk (Volatility) vs Expected Return scatter plot for portfolio assets.
    """
    chart = alt.Chart(df_port).mark_circle(size=250, opacity=0.9).encode(
        x=alt.X("Annual_Volatility_Pct:Q", title="Annual Volatility / Risk (%)", scale=alt.Scale(zero=False)),
        y=alt.Y("Expected_Annual_Return_Pct:Q", title="Expected Annual Return (%)", scale=alt.Scale(zero=False)),
        color=alt.Color("Asset_Class:N", scale=alt.Scale(scheme="category10"), legend=alt.Legend(title="Asset Class")),
        size=alt.Size("Current_Value_M:Q", title="Holding Value ($M)", scale=alt.Scale(range=[150, 750])),
        tooltip=[
            alt.Tooltip("Asset_Name:N", title="Asset"),
            alt.Tooltip("Ticker:N"),
            alt.Tooltip("Asset_Class:N", title="Class"),
            alt.Tooltip("Allocation_Pct:Q", title="Allocation (%)", format=".1f"),
            alt.Tooltip("Expected_Annual_Return_Pct:Q", title="Expected Return (%)", format=".1f"),
            alt.Tooltip("Annual_Volatility_Pct:Q", title="Volatility (%)", format=".1f"),
            alt.Tooltip("Current_Value_M:Q", title="Value ($M)", format="$,.2f")
        ]
    ).properties(height=360).interactive()
    
    text = chart.mark_text(align="left", dx=12, dy=-6, fontSize=11, color="#E2E8F0").encode(
        text="Ticker:N"
    )
    
    return chart + text

def make_portfolio_allocation_chart(df_port):
    """
    Bar chart showing allocation breakdown of the corporate treasury portfolio.
    """
    chart = alt.Chart(df_port).mark_bar(cornerRadius=5).encode(
        x=alt.X("Allocation_Pct:Q", title="Target Allocation (%)"),
        y=alt.Y("Asset_Name:N", sort="-x", title="Asset"),
        color=alt.Color("Asset_Class:N", scale=alt.Scale(scheme="set2"), legend=alt.Legend(title="Asset Class")),
        tooltip=[
            alt.Tooltip("Asset_Name:N"),
            alt.Tooltip("Allocation_Pct:Q", format=".1f"),
            alt.Tooltip("Current_Value_M:Q", format="$,.2f")
        ]
    ).properties(height=320)
    return chart

def make_monte_carlo_fan_chart(summary_df, sample_paths_df=None):
    """
    Fan chart with confidence percentile ribbons and median path.
    """
    # Ribbon from P10 to P90
    area_outer = alt.Chart(summary_df).mark_area(opacity=0.2, color="#3B82F6").encode(
        x=alt.X("Month:N", title="Forecast Horizon"),
        y=alt.Y("P10_Bearish:Q", title="Projected Metric ($)"),
        y2="P90_Bullish:Q"
    )
    
    # Ribbon from P25 to P75
    area_inner = alt.Chart(summary_df).mark_area(opacity=0.35, color="#3B82F6").encode(
        x="Month:N",
        y="P25_Conservative:Q",
        y2="P75_Optimistic:Q"
    )
    
    # Median line
    line_median = alt.Chart(summary_df).mark_line(color="#60A5FA", strokeWidth=3).encode(
        x="Month:N",
        y=alt.Y("P50_Median:Q", axis=alt.Axis(format="$,.0f")),
        tooltip=[
            alt.Tooltip("Month:N"),
            alt.Tooltip("P10_Bearish:Q", title="P10 (Worst 10%)", format="$,.0f"),
            alt.Tooltip("P50_Median:Q", title="Median Forecast", format="$,.0f"),
            alt.Tooltip("P90_Bullish:Q", title="P90 (Best 10%)", format="$,.0f")
        ]
    )
    
    chart = (area_outer + area_inner + line_median).properties(height=380).interactive()
    return chart

def make_audit_scatter_chart(df_tx):
    """
    Scatter plot of transactions over time highlighting flagged anomalies.
    """
    df = df_tx.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    
    color_scale = alt.Scale(
        domain=["Yes", "No"],
        range=["#EF4444", "#10B981"]
    )
    
    chart = alt.Chart(df).mark_circle(opacity=0.75).encode(
        x=alt.X("Date:T", title="Transaction Date"),
        y=alt.Y("Amount:Q", title="Amount ($)", scale=alt.Scale(type="log"), axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Is_Anomaly:N", scale=color_scale, legend=alt.Legend(title="Anomaly Flag")),
        size=alt.Size("Risk_Score:Q", title="Risk Score", scale=alt.Scale(range=[40, 320])),
        tooltip=[
            alt.Tooltip("Transaction_ID:N"),
            alt.Tooltip("Date:T", format="%Y-%m-%d"),
            alt.Tooltip("Department:N"),
            alt.Tooltip("Vendor:N"),
            alt.Tooltip("Amount:Q", format="$,.2f"),
            alt.Tooltip("Risk_Score:Q"),
            alt.Tooltip("Is_Anomaly:N"),
            alt.Tooltip("Anomaly_Reason:N")
        ]
    ).properties(height=360).interactive()
    
    return chart
