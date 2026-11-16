"""
Financial Analytics & Quantitative Risk Modeling Engine
Contains formulas for Financial KPIs, Ratios, Anomaly Detection, Portfolio Risk, and Monte Carlo Simulations.
"""

import numpy as np
import pandas as pd

def calculate_kpis(df):
    """
    Calculate top-level financial KPIs from the filtered financial dataframe.
    """
    if df.empty:
        return {}
    
    total_revenue = df["Revenue"].sum()
    total_cogs = df["COGS"].sum()
    gross_profit = df["Gross_Profit"].sum()
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue else 0
    
    total_opex = df["Total_OPEX"].sum()
    ebitda = df["EBITDA"].sum()
    ebitda_margin = (ebitda / total_revenue * 100) if total_revenue else 0
    
    net_income = df["Net_Income"].sum()
    net_margin = (net_income / total_revenue * 100) if total_revenue else 0
    
    fcf = df["Free_Cash_Flow"].sum()
    operating_cf = df["Operating_Cash_Flow"].sum()
    
    # Most recent snapshot items
    df_sorted = df.sort_values("Date")
    latest_row = df_sorted.iloc[-1]
    
    cash = latest_row["Cash_Equivalents"]
    current_assets = latest_row["Current_Assets"]
    current_liabilities = latest_row["Current_Liabilities"]
    total_debt = latest_row["Total_Debt"]
    total_equity = latest_row["Total_Equity"]
    
    current_ratio = (current_assets / current_liabilities) if current_liabilities > 0 else 0
    debt_to_equity = (total_debt / total_equity) if total_equity > 0 else 0
    
    # Monthly burn & Runway calculation
    # Average monthly net cash flow over last 6 periods
    recent_fcf = df_sorted.groupby("Date")["Free_Cash_Flow"].sum().tail(6)
    avg_monthly_fcf = recent_fcf.mean()
    if avg_monthly_fcf < 0:
        runway_months = cash / abs(avg_monthly_fcf)
    else:
        runway_months = 999.0 # Cash generative / self-sustaining
        
    # Growth metrics (YoY)
    # Aggregate monthly revenue
    monthly_rev = df.groupby("Date")["Revenue"].sum().sort_index()
    if len(monthly_rev) >= 13:
        current_period_rev = monthly_rev.iloc[-1]
        prior_year_rev = monthly_rev.iloc[-13]
        yoy_growth = ((current_period_rev - prior_year_rev) / prior_year_rev * 100) if prior_year_rev else 0
    elif len(monthly_rev) >= 2:
        current_period_rev = monthly_rev.iloc[-1]
        prior_rev = monthly_rev.iloc[-2]
        yoy_growth = ((current_period_rev - prior_rev) / prior_rev * 100) if prior_rev else 0
    else:
        yoy_growth = 0.0

    # SaaS Unit economics (weighted averages)
    avg_cac = df["CAC"].mean()
    avg_ltv = df["LTV"].mean()
    ltv_cac = (avg_ltv / avg_cac) if avg_cac else 0
    churn = df["Churn_Rate_Pct"].mean()
    
    return {
        "Total_Revenue": total_revenue,
        "Gross_Profit": gross_profit,
        "Gross_Margin_Pct": gross_margin,
        "Total_OPEX": total_opex,
        "EBITDA": ebitda,
        "EBITDA_Margin_Pct": ebitda_margin,
        "Net_Income": net_income,
        "Net_Margin_Pct": net_margin,
        "Free_Cash_Flow": fcf,
        "Operating_Cash_Flow": operating_cf,
        "Cash_Balance": cash,
        "Current_Ratio": current_ratio,
        "Debt_to_Equity": debt_to_equity,
        "Monthly_Burn": avg_monthly_fcf,
        "Runway_Months": runway_months,
        "YoY_Growth_Pct": yoy_growth,
        "LTV_CAC_Ratio": ltv_cac,
        "Avg_CAC": avg_cac,
        "Avg_LTV": avg_ltv,
        "Churn_Rate_Pct": churn
    }

def detect_anomalies(df, col="Amount", group_col="Category", threshold=2.5):
    """
    Detect statistical outliers using Modified Z-Score or Standard Z-Score per group.
    """
    df_copy = df.copy()
    
    def group_z_score(group):
        mean = group[col].mean()
        std = group[col].std()
        if std == 0 or np.isnan(std):
            group["Z_Score"] = 0.0
        else:
            group["Z_Score"] = (group[col] - mean) / std
        return group
        
    df_flagged = df_copy.groupby(group_col, group_keys=False).apply(group_z_score)
    df_flagged["Stat_Anomaly"] = df_flagged["Z_Score"].abs() > threshold
    return df_flagged

def calculate_portfolio_metrics(df_port, risk_free_rate=0.042):
    """
    Compute portfolio metrics: Weighted Return, Volatility, Sharpe Ratio, Sortino Ratio, Value at Risk.
    """
    weights = df_port["Allocation_Pct"].values / 100.0
    returns = df_port["Expected_Annual_Return_Pct"].values / 100.0
    vols = df_port["Annual_Volatility_Pct"].values / 100.0
    betas = df_port["Beta"].values
    
    # Portfolio expected return
    port_return = np.sum(weights * returns)
    
    # Correlation approximation: diversification benefit factor
    # public equities & tech have higher correlation (~0.7), bonds negative/low (~0.05), gold (~0.15)
    # simplified conservative covariance proxy:
    corr_matrix = np.full((len(weights), len(weights)), 0.25)
    np.fill_diagonal(corr_matrix, 1.0)
    
    # covariance matrix
    cov_matrix = np.outer(vols, vols) * corr_matrix
    port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    port_vol = np.sqrt(max(0.0001, port_variance))
    
    # Portfolio Beta
    port_beta = np.sum(weights * betas)
    
    # Sharpe Ratio
    excess_return = port_return - risk_free_rate
    sharpe = excess_return / port_vol if port_vol > 0 else 0
    
    # Downside deviation approximation for Sortino Ratio
    downside_vol = port_vol * 0.70
    sortino = excess_return / downside_vol if downside_vol > 0 else 0
    
    # Value at Risk (VaR 1-year holding period, normal distribution assumption)
    # 95% confidence Z = 1.645, 99% confidence Z = 2.326
    total_val_m = df_port["Current_Value_M"].sum()
    var_95_pct = -(port_return - 1.645 * port_vol)
    var_99_pct = -(port_return - 2.326 * port_vol)
    
    var_95_m = max(0, var_95_pct * total_val_m)
    var_99_m = max(0, var_99_pct * total_val_m)
    
    # Maximum Drawdown proxy (estimated from volatility)
    max_dd_est = 2.1 * port_vol * 100
    
    return {
        "Total_Portfolio_Value_M": total_val_m,
        "Weighted_Return_Pct": port_return * 100,
        "Weighted_Volatility_Pct": port_vol * 100,
        "Sharpe_Ratio": sharpe,
        "Sortino_Ratio": sortino,
        "Portfolio_Beta": port_beta,
        "VaR_95_Pct": max(0, var_95_pct * 100),
        "VaR_99_Pct": max(0, var_99_pct * 100),
        "VaR_95_Value_M": var_95_m,
        "VaR_99_Value_M": var_99_m,
        "Estimated_Max_Drawdown_Pct": min(100.0, max_dd_est)
    }

def run_monte_carlo_forecast(initial_val, monthly_growth_mean=0.018, monthly_vol=0.045, n_months=24, n_simulations=500, seed=42):
    """
    Run Monte Carlo stochastic forecast for revenue or cash balance.
    Returns simulation percentiles and sample paths.
    """
    np.random.seed(seed)
    # Geometric Brownian Motion simulation
    dt = 1.0
    drift = (monthly_growth_mean - 0.5 * (monthly_vol ** 2)) * dt
    diffusion = monthly_vol * np.sqrt(dt)
    
    paths = np.zeros((n_simulations, n_months + 1))
    paths[:, 0] = initial_val
    
    for t in range(1, n_months + 1):
        rand_shocks = np.random.normal(0, 1, n_simulations)
        paths[:, t] = paths[:, t-1] * np.exp(drift + diffusion * rand_shocks)
        
    months_axis = [f"M+{i}" for i in range(n_months + 1)]
    
    p10 = np.percentile(paths, 10, axis=0)
    p25 = np.percentile(paths, 25, axis=0)
    p50 = np.percentile(paths, 50, axis=0) # Median
    p75 = np.percentile(paths, 75, axis=0)
    p90 = np.percentile(paths, 90, axis=0)
    mean_path = np.mean(paths, axis=0)
    
    summary_df = pd.DataFrame({
        "Month": months_axis,
        "P10_Bearish": p10,
        "P25_Conservative": p25,
        "P50_Median": p50,
        "Mean_Expected": mean_path,
        "P75_Optimistic": p75,
        "P90_Bullish": p90
    })
    
    # Pick 8 sample paths for visualization overlay
    sample_paths_df = pd.DataFrame(paths[:8].T, columns=[f"Simulation_{i+1}" for i in range(8)])
    sample_paths_df["Month"] = months_axis
    
    return summary_df, sample_paths_df
