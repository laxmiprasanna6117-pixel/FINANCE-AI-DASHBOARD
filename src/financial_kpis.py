import pandas as pd
import numpy as np

class FinancialKPIEngine:
    """
    Computes dynamic financial KPIs, variance metrics, aggregations,
    and Chart.js-ready data series based on user filters and available columns.
    """

    def __init__(self, df, schema_metadata=None):
        self.raw_df = df
        self.metadata = schema_metadata or {}

    def filter_data(self, start_date=None, end_date=None, category=None, search=None):
        """Applies interactive filters to the dataset."""
        df = self.raw_df.copy()

        # Date range filter
        if '__parsed_date' in df.columns:
            if start_date:
                try:
                    s_dt = pd.to_datetime(start_date)
                    df = df[df['__parsed_date'] >= s_dt]
                except Exception:
                    pass
            if end_date:
                try:
                    e_dt = pd.to_datetime(end_date)
                    df = df[df['__parsed_date'] <= e_dt]
                except Exception:
                    pass

        # Category filter
        if category and category.lower() != 'all' and '__category' in df.columns:
            df = df[df['__category'].astype(str).str.lower() == category.lower()]

        # Search filter
        if search and search.strip():
            query = search.strip().lower()
            mask = False
            for col in df.columns:
                if not col.startswith('__'):
                    mask = mask | df[col].astype(str).str.lower().str.contains(query, regex=False)
            df = df[mask]

        return df

    def calculate_kpis(self, df):
        """Calculates core executive financial metrics."""
        if df.empty:
            return {
                'total_revenue': 0.0,
                'total_expenses': 0.0,
                'net_profit': 0.0,
                'profit_margin_pct': 0.0,
                'total_transactions': 0,
                'avg_transaction_value': 0.0,
                'has_budget': False,
                'total_budget': 0.0,
                'budget_variance': 0.0,
                'budget_variance_pct': 0.0,
                'has_status': False
            }

        total_revenue = float(df['__revenue'].sum()) if '__revenue' in df.columns else 0.0
        total_expenses = float(df['__expense'].sum()) if '__expense' in df.columns else 0.0
        net_profit = float(df['__profit'].sum()) if '__profit' in df.columns else (total_revenue - total_expenses)
        
        profit_margin = (net_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0
        total_transactions = int(len(df))
        
        if total_revenue > 0:
            avg_tx = total_revenue / total_transactions
        elif total_expenses > 0:
            avg_tx = total_expenses / total_transactions
        else:
            avg_tx = 0.0

        has_budget = bool('__budget' in df.columns and float(df['__budget'].sum()) > 0)
        total_budget = float(df['__budget'].sum()) if has_budget else 0.0
        budget_variance = float(total_budget - total_expenses) if has_budget else 0.0
        budget_variance_pct = float((budget_variance / total_budget) * 100.0) if has_budget and total_budget > 0 else 0.0

        has_status = bool('__status' in df.columns and int(df['__status'].nunique()) > 1)

        return {
            'total_revenue': round(total_revenue, 2),
            'total_expenses': round(total_expenses, 2),
            'net_profit': round(net_profit, 2),
            'profit_margin_pct': round(profit_margin, 2),
            'total_transactions': total_transactions,
            'avg_transaction_value': round(avg_tx, 2),
            'has_budget': has_budget,
            'total_budget': round(total_budget, 2),
            'budget_variance': round(budget_variance, 2),
            'budget_variance_pct': round(budget_variance_pct, 2),
            'has_status': has_status
        }

    def get_time_series_data(self, df, frequency='monthly'):
        """Aggregates revenue, expenses, and profit by time periods."""
        if '__parsed_date' not in df.columns or df['__parsed_date'].dropna().empty:
            n_bins = min(12, max(1, len(df)))
            df = df.copy()
            df['__bin'] = pd.qcut(range(len(df)), q=n_bins, labels=[f"Batch {i+1}" for i in range(n_bins)])
            grouped = df.groupby('__bin', observed=False)[['__revenue', '__expense', '__profit']].sum().reset_index()
            return {
                'labels': grouped['__bin'].tolist(),
                'revenue': [round(float(x), 2) for x in grouped['__revenue'].tolist()],
                'expenses': [round(float(x), 2) for x in grouped['__expense'].tolist()],
                'profit': [round(float(x), 2) for x in grouped['__profit'].tolist()],
                'cumulative_revenue': [round(float(x), 2) for x in grouped['__revenue'].cumsum().tolist()],
                'cumulative_expenses': [round(float(x), 2) for x in grouped['__expense'].cumsum().tolist()]
            }

        df_valid = df.dropna(subset=['__parsed_date']).copy()
        if df_valid.empty:
            return {'labels': [], 'revenue': [], 'expenses': [], 'profit': [], 'cumulative_revenue': [], 'cumulative_expenses': []}

        df_valid.sort_values('__parsed_date', inplace=True)

        if frequency == 'yearly':
            group_col = '__year'
        elif frequency == 'quarterly':
            group_col = '__quarter'
        else:
            group_col = '__year_month'

        grouped = df_valid.groupby(group_col, observed=True)[['__revenue', '__expense', '__profit']].sum().reset_index()

        labels = [str(x) for x in grouped[group_col].tolist()]
        rev = [round(float(x), 2) for x in grouped['__revenue'].tolist()]
        exp = [round(float(x), 2) for x in grouped['__expense'].tolist()]
        prof = [round(float(x), 2) for x in grouped['__profit'].tolist()]
        cum_rev = [round(float(x), 2) for x in grouped['__revenue'].cumsum().tolist()]
        cum_exp = [round(float(x), 2) for x in grouped['__expense'].cumsum().tolist()]

        return {
            'labels': labels,
            'revenue': rev,
            'expenses': exp,
            'profit': prof,
            'cumulative_revenue': cum_rev,
            'cumulative_expenses': cum_exp
        }

    def get_category_breakdown(self, df, limit=10):
        """Computes revenue and expense totals per category."""
        if '__category' not in df.columns:
            return {'revenue_categories': {'labels': [], 'values': []}, 'expense_categories': {'labels': [], 'values': []}}

        rev_grouped = df.groupby('__category')[['__revenue']].sum().reset_index()
        rev_grouped = rev_grouped[rev_grouped['__revenue'] > 0].sort_values('__revenue', ascending=False).head(limit)

        exp_grouped = df.groupby('__category')[['__expense']].sum().reset_index()
        exp_grouped = exp_grouped[exp_grouped['__expense'] > 0].sort_values('__expense', ascending=False).head(limit)

        return {
            'revenue_categories': {
                'labels': rev_grouped['__category'].tolist(),
                'values': [round(float(x), 2) for x in rev_grouped['__revenue'].tolist()]
            },
            'expense_categories': {
                'labels': exp_grouped['__category'].tolist(),
                'values': [round(float(x), 2) for x in exp_grouped['__expense'].tolist()]
            }
        }

    def get_budget_vs_actual(self, df, limit=8):
        """Compares budget vs actual expenses across categories."""
        if '__budget' not in df.columns or '__category' not in df.columns:
            return {'labels': [], 'budget': [], 'actual': [], 'variance': []}

        grouped = df.groupby('__category')[['__budget', '__expense']].sum().reset_index()
        grouped['variance'] = grouped['__budget'] - grouped['__expense']
        grouped = grouped.sort_values('__budget', ascending=False).head(limit)

        return {
            'labels': grouped['__category'].tolist(),
            'budget': [round(float(x), 2) for x in grouped['__budget'].tolist()],
            'actual': [round(float(x), 2) for x in grouped['__expense'].tolist()],
            'variance': [round(float(x), 2) for x in grouped['variance'].tolist()]
        }

    def get_payment_status_breakdown(self, df):
        """Analyzes transactions grouped by payment/invoice status."""
        if '__status' not in df.columns:
            return {'labels': [], 'counts': [], 'amounts': []}

        amount_col = '__revenue' if df['__revenue'].sum() > 0 else '__expense'
        grouped = df.groupby('__status').agg(
            count=('__status', 'count'),
            amount=(amount_col, 'sum')
        ).reset_index().sort_values('count', ascending=False)

        return {
            'labels': grouped['__status'].tolist(),
            'counts': grouped['count'].tolist(),
            'amounts': [round(float(x), 2) for x in grouped['amount'].tolist()]
        }

    def get_filter_options(self):
        """Returns available filter options for dropdowns."""
        df = self.raw_df
        categories = ['All']
        if '__category' in df.columns:
            cats = sorted([str(c) for c in df['__category'].dropna().unique() if str(c).strip()])
            categories.extend(cats)

        date_min, date_max = None, None
        if '__parsed_date' in df.columns and df['__parsed_date'].notna().any():
            date_min = df['__parsed_date'].min().strftime('%Y-%m-%d')
            date_max = df['__parsed_date'].max().strftime('%Y-%m-%d')

        return {
            'categories': categories,
            'min_date': date_min,
            'max_date': date_max,
            'total_records': len(df)
        }
