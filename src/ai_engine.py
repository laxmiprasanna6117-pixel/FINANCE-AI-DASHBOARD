import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest

class FinancialAIEngine:
    """
    Local AI & Statistical Intelligence Module.
    Performs anomaly detection (Isolation Forest & Z-scores), linear regression trend analysis,
    Pareto 80/20 concentration analysis, risk scoring, and data-backed recommendations.
    Uses strictly deterministic mathematical & machine learning methods (No external LLM APIs).
    """

    def __init__(self, df, kpis, time_series, category_data):
        self.df = df
        self.kpis = kpis
        self.time_series = time_series
        self.category_data = category_data

    def detect_anomalies(self, contamination=0.03):
        """
        Detects anomalous transactions using Isolation Forest and Statistical Z-Score.
        Returns a list of flagged anomalous records with severity and rationale.
        """
        df = self.df.copy()
        if len(df) < 6:
            return []

        target_col = '__expense' if df['__expense'].sum() > 0 else '__revenue'
        if target_col not in df.columns or df[target_col].std() == 0:
            return []

        vals = df[[target_col]].fillna(0.0)
        
        # 1. Isolation Forest
        try:
            iso = IsolationForest(contamination=max(0.01, min(0.10, contamination)), random_state=42)
            preds = iso.fit_predict(vals)
            df['__is_anomaly_iso'] = preds == -1
        except Exception:
            df['__is_anomaly_iso'] = False

        # 2. Z-Score calculation
        mean_val = vals[target_col].mean()
        std_val = vals[target_col].std()
        if std_val > 0:
            df['__z_score'] = (vals[target_col] - mean_val) / std_val
        else:
            df['__z_score'] = 0.0

        anomaly_mask = (df['__z_score'].abs() >= 2.2) | (df['__is_anomaly_iso'] & (df['__z_score'].abs() >= 1.8))
        anomalies_df = df[anomaly_mask].copy()

        results = []
        for idx, row in anomalies_df.head(15).iterrows():
            z = float(row.get('__z_score', 0.0))
            amt = float(row.get(target_col, 0.0))
            cat = str(row.get('__category', 'General'))
            
            date_str = "Row #" + str(idx)
            if '__parsed_date' in row and pd.notna(row['__parsed_date']):
                date_str = str(row['__parsed_date'])[:10]

            severity = 'High' if abs(z) >= 3.0 else 'Medium'
            ratio = (amt / mean_val) if mean_val > 0 else 0.0

            reason = f"{target_col.replace('__', '').title()} of ${amt:,.2f} is {abs(z):.1f} std deviations from average (${mean_val:,.2f}) [{ratio:.1f}x normal level]."
            
            results.append({
                'id': int(idx),
                'date': date_str,
                'category': cat,
                'metric': target_col.replace('__', '').title(),
                'amount': round(amt, 2),
                'z_score': round(z, 2),
                'severity': severity,
                'reason': reason
            })

        results.sort(key=lambda x: abs(x['z_score']), reverse=True)
        return results

    def analyze_trends(self):
        """
        Calculates linear regression slopes, compound growth rates,
        and momentum comparisons for Revenue and Expenses.
        """
        ts = self.time_series
        rev_series = ts.get('revenue', [])
        exp_series = ts.get('expenses', [])
        labels = ts.get('labels', [])

        n_periods = len(rev_series)
        if n_periods < 2:
            return {
                'has_trends': False,
                'message': 'Insufficient time periods to calculate temporal growth trends.'
            }

        x = np.arange(n_periods)

        # Revenue Regression
        rev_slope, rev_intercept, rev_r, rev_p, _ = stats.linregress(x, rev_series)
        rev_cmgr = 0.0
        if rev_series[0] > 0 and rev_series[-1] > 0:
            rev_cmgr = ((rev_series[-1] / rev_series[0]) ** (1.0 / (n_periods - 1)) - 1.0) * 100.0

        # Expense Regression
        exp_slope, exp_intercept, exp_r, exp_p, _ = stats.linregress(x, exp_series)
        exp_cmgr = 0.0
        if exp_series[0] > 0 and exp_series[-1] > 0:
            exp_cmgr = ((exp_series[-1] / exp_series[0]) ** (1.0 / (n_periods - 1)) - 1.0) * 100.0

        def trend_descriptor(slope, cmgr, r2):
            if cmgr > 8.0 or slope > 1000:
                return 'Strong Growth'
            elif cmgr > 1.5 or slope > 0:
                return 'Moderate Growth'
            elif cmgr < -8.0 or slope < -1000:
                return 'Steep Contraction'
            elif cmgr < -1.5 or slope < 0:
                return 'Moderate Contraction'
            else:
                return 'Stable'

        rev_trend = trend_descriptor(rev_slope, rev_cmgr, rev_r ** 2)
        exp_trend = trend_descriptor(exp_slope, exp_cmgr, exp_r ** 2)

        margin_expansion = bool(rev_slope >= exp_slope)

        return {
            'has_trends': True,
            'periods_count': n_periods,
            'first_period': labels[0],
            'last_period': labels[-1],
            'revenue_trend': rev_trend,
            'revenue_slope': round(float(rev_slope), 2),
            'revenue_cmgr_pct': round(float(rev_cmgr), 2),
            'revenue_r2': round(float(rev_r ** 2), 3),
            'expense_trend': exp_trend,
            'expense_slope': round(float(exp_slope), 2),
            'expense_cmgr_pct': round(float(exp_cmgr), 2),
            'expense_r2': round(float(exp_r ** 2), 3),
            'margin_expansion': margin_expansion
        }

    def analyze_category_concentration(self):
        """
        Pareto 80/20 analysis and concentration risk scoring.
        """
        cat_data = self.category_data
        rev_cats = cat_data.get('revenue_categories', {})
        exp_cats = cat_data.get('expense_categories', {})

        total_rev = self.kpis.get('total_revenue', 0.0)
        total_exp = self.kpis.get('total_expenses', 0.0)

        # Revenue concentration
        rev_concentration = []
        if total_rev > 0 and rev_cats.get('labels'):
            cum_share = 0.0
            for label, val in zip(rev_cats['labels'], rev_cats['values']):
                share = (val / total_rev) * 100.0
                cum_share += share
                rev_concentration.append({
                    'category': label,
                    'amount': val,
                    'share_pct': round(share, 1),
                    'cum_share_pct': round(cum_share, 1)
                })

        top_rev_cat = rev_concentration[0] if rev_concentration else None

        # Expense concentration
        exp_concentration = []
        if total_exp > 0 and exp_cats.get('labels'):
            cum_share = 0.0
            for label, val in zip(exp_cats['labels'], exp_cats['values']):
                share = (val / total_exp) * 100.0
                cum_share += share
                exp_concentration.append({
                    'category': label,
                    'amount': val,
                    'share_pct': round(share, 1),
                    'cum_share_pct': round(cum_share, 1)
                })

        top_exp_cat = exp_concentration[0] if exp_concentration else None

        high_rev_concentration = bool(top_rev_cat is not None and top_rev_cat['share_pct'] >= 45.0)
        high_exp_concentration = bool(top_exp_cat is not None and top_exp_cat['share_pct'] >= 45.0)

        return {
            'revenue_concentration': rev_concentration,
            'top_revenue_category': top_rev_cat,
            'high_revenue_concentration_risk': high_rev_concentration,
            'expense_concentration': exp_concentration,
            'top_expense_category': top_exp_cat,
            'high_expense_concentration_risk': high_exp_concentration
        }

    def generate_financial_risks(self, trends, concentration, anomalies):
        """Evaluates possible business & financial risks based on mathematical signals."""
        risks = []
        k = self.kpis

        # 1. Profitability & Burn Risk
        if k['net_profit'] < 0:
            risks.append({
                'title': 'Operating Deficit / Net Loss Alert',
                'severity': 'Critical',
                'description': f"Total expenses (${k['total_expenses']:,.2f}) exceed total revenue (${k['total_revenue']:,.2f}) resulting in a net deficit of ${abs(k['net_profit']):,.2f}.",
                'mitigation': 'Implement immediate expenditure caps on discretionary cost centers and accelerate collection on receivables.'
            })
        elif k['profit_margin_pct'] > 0 and k['profit_margin_pct'] < 8.0:
            risks.append({
                'title': 'Thin Profit Margin Exposure',
                'severity': 'Medium',
                'description': f"The net profit margin is {k['profit_margin_pct']:.1f}%, leaving minimal buffer against unexpected demand drops or cost inflation.",
                'mitigation': 'Review pricing strategies and optimize direct COGS/operating overhead.'
            })

        # 2. Expense Velocity vs Revenue Velocity
        if trends.get('has_trends') and not trends.get('margin_expansion', True):
            risks.append({
                'title': 'Margin Compression (Expenses Outpacing Revenue)',
                'severity': 'High',
                'description': f"Expense growth rate ({trends.get('expense_cmgr_pct', 0):.1f}%/period) exceeds revenue growth rate ({trends.get('revenue_cmgr_pct', 0):.1f}%/period).",
                'mitigation': 'Freeze non-essential hiring/procurement and re-align department budgets with revenue milestones.'
            })

        # 3. Revenue Concentration Risk
        if concentration.get('high_revenue_concentration_risk'):
            top_cat = concentration.get('top_revenue_category', {})
            risks.append({
                'title': 'High Revenue Source Concentration',
                'severity': 'High',
                'description': f"A single category/source ('{top_cat.get('category')}') generates {top_cat.get('share_pct', 0):.1f}% of all gross revenue.",
                'mitigation': 'Diversify commercial channels and expand complementary product lines to reduce dependence on a single pillar.'
            })

        # 4. Expense Concentration Risk
        if concentration.get('high_expense_concentration_risk'):
            top_exp = concentration.get('top_expense_category', {})
            risks.append({
                'title': 'Heavy Cost Center Concentration',
                'severity': 'Medium',
                'description': f"Cost center '{top_exp.get('category')}' consumes {top_exp.get('share_pct', 0):.1f}% of total enterprise expenditures (${top_exp.get('amount', 0):,.2f}).",
                'mitigation': 'Perform vendor renegotiations and audit vendor contract pricing.'
            })

        # 5. Anomaly Volatility Risk
        if len(anomalies) >= 3:
            total_anomaly_val = sum(a['amount'] for a in anomalies)
            risks.append({
                'title': 'Elevated Transaction Volatility / Audit Flags',
                'severity': 'Medium',
                'description': f"Detected {len(anomalies)} statistical anomalies totaling ${total_anomaly_val:,.2f} exceeding 2.2 standard deviations.",
                'mitigation': 'Conduct internal spot-audits on flagged transactions to rule out fraud, invoice errors, or unbudgeted capital outflows.'
            })

        # 6. Budget Overrun Risk
        if k.get('has_budget') and k.get('budget_variance', 0) < 0:
            risks.append({
                'title': 'Budget Overrun Detected',
                'severity': 'High',
                'description': f"Actual expenditures exceed budgeted allocations by ${abs(k['budget_variance']):,.2f} ({abs(k['budget_variance_pct']):.1f}% over budget).",
                'mitigation': 'Enforce procurement approval workflows for any spend exceeding monthly department quotas.'
            })

        if not risks:
            risks.append({
                'title': 'Balanced Financial Stability',
                'severity': 'Low',
                'description': 'Current data exhibits stable margins, controlled expenditures, and healthy variance metrics with no critical threats identified.',
                'mitigation': 'Maintain existing operational controls and re-evaluate during upcoming fiscal period.'
            })

        return risks

    def generate_recommendations(self, trends, concentration, anomalies, risks):
        """Synthesizes actionable, data-backed financial recommendations."""
        recommendations = []
        k = self.kpis

        top_exp = concentration.get('top_expense_category')
        if top_exp:
            potential_savings = top_exp['amount'] * 0.08
            recommendations.append({
                'category': 'Cost Rationalization',
                'title': f"Audit and Renegotiate '{top_exp['category']}' Spend",
                'impact': f"Potential estimated annual savings of ${potential_savings:,.2f}",
                'action': f"Conduct targeted contract renegotiations on '{top_exp['category']}', which currently represents {top_exp['share_pct']:.1f}% (${top_exp['amount']:,.2f}) of all expenditures."
            })

        top_rev = concentration.get('top_revenue_category')
        if top_rev:
            recommendations.append({
                'category': 'Revenue Expansion',
                'title': f"Scale Proven Performance in '{top_rev['category']}'",
                'impact': f"Capitalize on primary revenue engine ({top_rev['share_pct']:.1f}% contribution)",
                'action': f"Allocate additional commercial support to '{top_rev['category']}' while cross-selling adjacent lower-performing categories to balance the portfolio."
            })

        if anomalies:
            recommendations.append({
                'category': 'Financial Governance',
                'title': 'Investigate Flagged Outlier Transactions',
                'impact': f"Immediate oversight on {len(anomalies)} high-variance line items",
                'action': f"Review the {len(anomalies)} anomalous records flagged in the AI audit log to verify authorization and prevent recurring off-cycle leakages."
            })

        if trends.get('has_trends'):
            if not trends.get('margin_expansion', True):
                recommendations.append({
                    'category': 'Margin Defense',
                    'title': 'Constrain OPEX Growth Below Revenue Trajectory',
                    'impact': 'Prevents operating margin erosion over subsequent quarters',
                    'action': f"Cap expense growth at or below {max(0, trends.get('revenue_cmgr_pct', 0)):.1f}% until revenue acceleration stabilizes."
                })
            else:
                recommendations.append({
                    'category': 'Capital Reinvestment',
                    'title': 'Reinvest Operational Surplus in High-ROI Initiatives',
                    'impact': f"Healthy revenue trajectory ({trends.get('revenue_cmgr_pct', 0):.1f}% CMGR) supports selective growth investments",
                    'action': 'Channel a portion of operating profits into productive automation and capacity expansion.'
                })

        return recommendations

    def generate_executive_summary(self, trends, concentration, risks):
        """Constructs an intelligent executive natural-language financial narrative."""
        k = self.kpis
        margin = k['profit_margin_pct']
        profit = k['net_profit']
        
        status = "profitable" if profit >= 0 else "operating at an operating deficit"
        margin_desc = f"{margin:.1f}% net margin" if profit >= 0 else f"-{abs(margin):.1f}% negative margin"

        summary_parts = [
            f"The analyzed dataset encompasses {k['total_transactions']:,} records with total recognized revenue of ${k['total_revenue']:,.2f} "
            f"and total expenditures of ${k['total_expenses']:,.2f}. The business is currently {status} with a net result of ${profit:,.2f} ({margin_desc})."
        ]

        if trends.get('has_trends'):
            summary_parts.append(
                f"Revenue exhibits a {trends['revenue_trend'].lower()} trend (slope of ${trends['revenue_slope']:,.2f}/period, {trends['revenue_cmgr_pct']:.1f}% CMGR), "
                f"while expenditures are moving with a {trends['expense_trend'].lower()} trajectory ({trends['expense_cmgr_pct']:.1f}% CMGR)."
            )

        top_rev = concentration.get('top_revenue_category')
        top_exp = concentration.get('top_expense_category')
        if top_rev and top_exp:
            summary_parts.append(
                f"Primary commercial performance is anchored by '{top_rev['category']}' (${top_rev['amount']:,.2f}, {top_rev['share_pct']:.1f}% share), "
                f"while the leading cost driver is '{top_exp['category']}' (${top_exp['amount']:,.2f}, {top_exp['share_pct']:.1f}% of total spend)."
            )

        critical_risks = [r for r in risks if r['severity'] in ('Critical', 'High')]
        if critical_risks:
            summary_parts.append(
                f"Key executive attention is advised regarding {len(critical_risks)} elevated risk factor(s), primarily: {critical_risks[0]['title']}."
            )
        else:
            summary_parts.append("Financial health indicators reflect balanced operations with controlled spending patterns.")

        return " ".join(summary_parts)

    def run_full_analysis(self):
        """Runs the complete AI analytics pipeline and compiles results."""
        anomalies = self.detect_anomalies()
        trends = self.analyze_trends()
        concentration = self.analyze_category_concentration()
        risks = self.generate_financial_risks(trends, concentration, anomalies)
        recommendations = self.generate_recommendations(trends, concentration, anomalies, risks)
        summary = self.generate_executive_summary(trends, concentration, risks)

        return {
            'anomalies': anomalies,
            'trends': trends,
            'concentration': concentration,
            'risks': risks,
            'recommendations': recommendations,
            'executive_summary': summary
        }
