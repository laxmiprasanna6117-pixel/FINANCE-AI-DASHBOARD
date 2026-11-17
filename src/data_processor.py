import io
import re
import os
import pandas as pd
import numpy as np
from datetime import datetime

class DataProcessor:
    """
    Intelligent financial dataset processor.
    Detects financial fields, cleans data, handles currency formatting,
    identifies data quality issues, and prepares standardized financial tables.
    """

    REVENUE_KEYWORDS = [
        'revenue', 'sales', 'turnover', 'gross_sales', 'income', 'earnings', 
        'inflow', 'amount_in', 'credit', 'credits', 'gross_revenue', 'net_sales',
        'billings', 'receipts', 'top_line', 'collections'
    ]

    EXPENSE_KEYWORDS = [
        'actual_expense', 'expense', 'expenses', 'expenditure', 'costs', 'cogs', 'spending',
        'outflow', 'amount_out', 'debit', 'debits', 'disbursement', 'fees', 'bills',
        'operating_expense', 'opex', 'payroll', 'overhead', 'purchase', 'payout', 'cost'
    ]

    PROFIT_KEYWORDS = [
        'profit', 'net_profit', 'gross_profit', 'net_income', 'operating_income',
        'ebitda', 'ebit', 'margin', 'net_earnings', 'bottom_line', 'retained_earnings'
    ]

    AMOUNT_KEYWORDS = [
        'amount', 'total', 'transaction_amount', 'value', 'price', 'net_amount',
        'invoice_amount', 'payment_amount', 'balance', 'sum', 'charge'
    ]

    BUDGET_KEYWORDS = [
        'budget', 'budgeted', 'target', 'planned', 'plan', 'forecast', 'quota',
        'allocated', 'allocation', 'projected'
    ]

    DATE_KEYWORDS = [
        'date', 'transaction_date', 'invoice_date', 'timestamp', 'period',
        'posting_date', 'payment_date', 'order_date', 'time', 'day', 'month', 'year'
    ]

    CATEGORY_KEYWORDS = [
        'cost_center', 'expense_category', 'revenue_category', 'category', 'department', 'dept',
        'account', 'type', 'segment', 'division', 'line_item',
        'item', 'product', 'service', 'classification', 'group', 'sector'
    ]

    TYPE_KEYWORDS = [
        'type', 'transaction_type', 'flow', 'direction', 'entry_type',
        'payment_type', 'record_type'
    ]

    STATUS_KEYWORDS = [
        'status', 'payment_status', 'state', 'invoice_status', 'order_status',
        'approval_status', 'settlement_status'
    ]

    ENTITY_KEYWORDS = [
        'vendor', 'supplier', 'merchant', 'payee', 'customer', 'client',
        'party', 'payer', 'partner', 'company', 'counterparty'
    ]

    def __init__(self):
        self.raw_df = None
        self.cleaned_df = None
        self.schema = {}
        self.quality_report = {}

    @staticmethod
    def _clean_currency_string(val):
        """Clean currency strings like '$1,234.56', '(500.00)', '€ 1.200,50' into float."""
        if pd.isna(val):
            return np.nan
        if isinstance(val, (int, float, np.integer, np.floating)):
            return float(val)
        
        s = str(val).strip()
        if not s:
            return np.nan

        is_negative = False
        if s.startswith('(') and s.endswith(')'):
            is_negative = True
            s = s[1:-1].strip()
        elif s.startswith('-') or s.endswith('-'):
            is_negative = True
            s = s.replace('-', '').strip()

        # Remove currency symbols and non-numeric characters (except separators)
        s = re.sub(r'[$€£₹¥A-Za-z\s]', '', s)

        if '.' in s and ',' in s:
            if s.rfind(',') > s.rfind('.'):
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        elif ',' in s and '.' not in s:
            parts = s.split(',')
            if len(parts) == 2 and len(parts[1]) in (2, 3) and len(parts[0]) <= 3:
                s = s.replace(',', '.')
            else:
                s = s.replace(',', '')

        try:
            val_float = float(s)
            return -val_float if is_negative else val_float
        except ValueError:
            return np.nan

    def _is_numeric_compatible(self, series):
        """Checks if a series contains numeric values or parseable currency strings."""
        if pd.api.types.is_numeric_dtype(series):
            return True
        sample = series.dropna().head(20)
        if len(sample) == 0:
            return False
        valid_count = 0
        for x in sample:
            cleaned = self._clean_currency_string(x)
            if not pd.isna(cleaned):
                valid_count += 1
        return valid_count >= max(1, len(sample) * 0.6)

    def load_file(self, file_path_or_buffer, filename=None):
        """Read CSV or Excel file safely with auto-detection."""
        if filename is None:
            filename = getattr(file_path_or_buffer, 'filename', '') or str(file_path_or_buffer)

        lower_name = filename.lower()
        df = None

        if lower_name.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(file_path_or_buffer)
            except Exception as e:
                raise ValueError(f"Failed to read Excel file: {str(e)}")
        else:
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'iso-8859-1', 'cp1252']
            success = False
            last_err = None

            for enc in encodings:
                try:
                    if hasattr(file_path_or_buffer, 'seek'):
                        file_path_or_buffer.seek(0)
                    df = pd.read_csv(file_path_or_buffer, encoding=enc, sep=None, engine='python')
                    success = True
                    break
                except Exception as e:
                    last_err = e
                    continue

            if not success:
                raise ValueError(f"Failed to parse CSV file: {str(last_err)}")

        if df is None or df.empty:
            raise ValueError("The uploaded file contains no data.")

        self.raw_df = df
        return df

    def detect_schema(self, df):
        """Fuzzy semantic mapping for financial column roles with type validation."""
        columns = list(df.columns)
        normalized_cols = {col: re.sub(r'[^a-z0-9]', '_', str(col).lower().strip()).strip('_') for col in columns}

        role_candidates = {
            'date': None,
            'revenue': None,
            'expense': None,
            'profit': None,
            'amount': None,
            'budget': None,
            'category': None,
            'type': None,
            'status': None,
            'entity': None
        }

        # Match columns against keywords
        for orig_col, norm_col in normalized_cols.items():
            is_numeric = self._is_numeric_compatible(df[orig_col])

            # 1. Date Detection
            if not role_candidates['date']:
                if any(kw in norm_col for kw in self.DATE_KEYWORDS):
                    role_candidates['date'] = orig_col
                elif pd.api.types.is_datetime64_any_dtype(df[orig_col]):
                    role_candidates['date'] = orig_col

            # 2. Revenue Detection (must be numeric compatible)
            if not role_candidates['revenue'] and is_numeric:
                if any(kw in norm_col for kw in self.REVENUE_KEYWORDS) and 'category' not in norm_col and 'type' not in norm_col:
                    role_candidates['revenue'] = orig_col

            # 3. Expense Detection (must be numeric compatible)
            if not role_candidates['expense'] and is_numeric:
                # Avoid classifying 'cost_center' as expense amount
                if 'cost_center' not in norm_col and 'category' not in norm_col and 'type' not in norm_col:
                    if any(kw in norm_col for kw in self.EXPENSE_KEYWORDS):
                        role_candidates['expense'] = orig_col

            # 4. Profit Detection (must be numeric compatible)
            if not role_candidates['profit'] and is_numeric:
                if any(kw in norm_col for kw in self.PROFIT_KEYWORDS) and 'margin_pct' not in norm_col:
                    role_candidates['profit'] = orig_col

            # 5. Budget Detection (must be numeric compatible)
            if not role_candidates['budget'] and is_numeric:
                if any(kw in norm_col for kw in self.BUDGET_KEYWORDS):
                    role_candidates['budget'] = orig_col

            # 6. General Amount Detection (must be numeric compatible)
            if not role_candidates['amount'] and is_numeric:
                if any(kw in norm_col for kw in self.AMOUNT_KEYWORDS) and orig_col not in (role_candidates['revenue'], role_candidates['expense'], role_candidates['budget']):
                    role_candidates['amount'] = orig_col

            # 7. Type Detection
            if not role_candidates['type']:
                if any(kw in norm_col for kw in self.TYPE_KEYWORDS):
                    role_candidates['type'] = orig_col

            # 8. Status Detection
            if not role_candidates['status']:
                if any(kw in norm_col for kw in self.STATUS_KEYWORDS):
                    role_candidates['status'] = orig_col

            # 9. Category Detection
            if not role_candidates['category'] and not is_numeric:
                if any(kw in norm_col for kw in self.CATEGORY_KEYWORDS):
                    role_candidates['category'] = orig_col

            # 10. Entity Detection
            if not role_candidates['entity'] and not is_numeric:
                if any(kw in norm_col for kw in self.ENTITY_KEYWORDS):
                    role_candidates['entity'] = orig_col

        # Fallback date detection
        if not role_candidates['date']:
            for col in columns:
                if df[col].dtype == object:
                    sample = df[col].dropna().head(10)
                    if len(sample) > 0:
                        try:
                            pd.to_datetime(sample, errors='raise')
                            role_candidates['date'] = col
                            break
                        except Exception:
                            pass

        # Fallback category detection
        if not role_candidates['category']:
            for col in columns:
                if col not in (role_candidates['date'], role_candidates['type'], role_candidates['status']):
                    if not self._is_numeric_compatible(df[col]):
                        nunique = df[col].nunique()
                        if 1 < nunique <= max(50, int(len(df) * 0.5)):
                            role_candidates['category'] = col
                            break

        # Fallback amount detection
        if not role_candidates['revenue'] and not role_candidates['expense'] and not role_candidates['amount']:
            for col in columns:
                if col != role_candidates['date'] and self._is_numeric_compatible(df[col]):
                    role_candidates['amount'] = col
                    break

        self.schema = role_candidates
        return role_candidates

    def process_and_clean(self, df=None):
        """Thoroughly cleans and standardizes the dataset."""
        if df is None:
            df = self.raw_df

        if df is None or df.empty:
            raise ValueError("No data to process.")

        df = df.copy()

        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)

        initial_row_count = len(df)
        duplicates_count = int(df.duplicated().sum())
        df.drop_duplicates(inplace=True)

        schema = self.detect_schema(df)

        financial_cols = [schema['revenue'], schema['expense'], schema['profit'], schema['amount'], schema['budget']]
        financial_cols = [c for c in financial_cols if c is not None and c in df.columns]

        for col in financial_cols:
            if df[col].dtype == object:
                df[col] = df[col].apply(self._clean_currency_string)
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        date_col = schema['date']
        has_valid_dates = False
        if date_col and date_col in df.columns:
            try:
                df['__parsed_date'] = pd.to_datetime(df[date_col], errors='coerce')
                valid_date_count = df['__parsed_date'].notna().sum()
                if valid_date_count >= len(df) * 0.4:
                    has_valid_dates = True
                    df['__year'] = df['__parsed_date'].dt.year
                    df['__month'] = df['__parsed_date'].dt.month
                    df['__year_month'] = df['__parsed_date'].dt.to_period('M').astype(str)
                    df['__quarter'] = df['__parsed_date'].dt.to_period('Q').astype(str)
                else:
                    df.drop(columns=['__parsed_date'], inplace=True, errors='ignore')
            except Exception:
                pass

        # Standardize Revenue, Expense, Profit
        if schema['revenue'] and schema['expense']:
            df['__revenue'] = df[schema['revenue']].fillna(0.0)
            df['__expense'] = df[schema['expense']].fillna(0.0)
            if schema['profit'] and schema['profit'] in df.columns:
                df['__profit'] = df[schema['profit']].fillna(df['__revenue'] - df['__expense'])
            else:
                df['__profit'] = df['__revenue'] - df['__expense']

        elif schema['amount'] and schema['type']:
            amount_series = df[schema['amount']].fillna(0.0)
            type_series = df[schema['type']].astype(str).str.lower().str.strip()

            is_income = type_series.str.contains('income|revenue|credit|sale|inflow|deposit', regex=True)
            is_expense = type_series.str.contains('expense|cost|debit|outflow|payment|charge|withdrawal', regex=True)

            df['__revenue'] = np.where(is_income, amount_series.abs(), 0.0)
            df['__expense'] = np.where(is_expense, amount_series.abs(), 0.0)
            df['__profit'] = df['__revenue'] - df['__expense']

        elif schema['amount']:
            amount_series = df[schema['amount']].fillna(0.0)
            neg_count = (amount_series < 0).sum()

            if neg_count > 0:
                df['__revenue'] = np.where(amount_series > 0, amount_series, 0.0)
                df['__expense'] = np.where(amount_series < 0, amount_series.abs(), 0.0)
                df['__profit'] = df['__revenue'] - df['__expense']
            else:
                df['__revenue'] = amount_series
                df['__expense'] = 0.0
                df['__profit'] = amount_series

        elif schema['revenue']:
            df['__revenue'] = df[schema['revenue']].fillna(0.0)
            df['__expense'] = 0.0
            df['__profit'] = df['__revenue']

        elif schema['expense']:
            df['__revenue'] = 0.0
            df['__expense'] = df[schema['expense']].fillna(0.0)
            df['__profit'] = -df['__expense']

        else:
            df['__revenue'] = 0.0
            df['__expense'] = 0.0
            df['__profit'] = 0.0

        cat_col = schema['category']
        if cat_col and cat_col in df.columns:
            df['__category'] = df[cat_col].fillna('Uncategorized').astype(str).str.strip()
        else:
            df['__category'] = 'General'

        if schema['budget'] and schema['budget'] in df.columns:
            df['__budget'] = pd.to_numeric(df[schema['budget']], errors='coerce').fillna(0.0)

        if schema['status'] and schema['status'] in df.columns:
            df['__status'] = df[schema['status']].fillna('Unknown').astype(str).str.strip()

        total_cells = df.shape[0] * df.shape[1]
        missing_cells = int(df.isna().sum().sum())
        missing_rate = (missing_cells / total_cells) if total_cells > 0 else 0.0

        outlier_count = 0
        for col in ['__revenue', '__expense', '__profit']:
            series = df[col].dropna()
            if len(series) > 10:
                q25, q75 = series.quantile(0.25), series.quantile(0.75)
                iqr = q75 - q25
                if iqr > 0:
                    lower_bound = q25 - (2.5 * iqr)
                    upper_bound = q75 + (2.5 * iqr)
                    outlier_count += int(((series < lower_bound) | (series > upper_bound)).sum())

        has_financial_data = bool(schema['revenue'] or schema['expense'] or schema['amount'] or schema['profit'])
        total_rows_cleaned = len(df)

        quality_score = 100.0
        if not has_financial_data:
            quality_score -= 50.0
        if missing_rate > 0.1:
            quality_score -= min(30.0, missing_rate * 50)
        if duplicates_count > 0:
            quality_score -= min(15.0, (duplicates_count / initial_row_count) * 30)
        if not has_valid_dates:
            quality_score -= 10.0
        quality_score = max(10.0, round(quality_score, 1))

        missing_info_diagnosis = []
        if not has_financial_data:
            missing_info_diagnosis.append(
                "No financial amount, revenue, or expense columns were found. "
                "Ensure your CSV or Excel file has columns indicating amounts, sales, or costs."
            )
        if not has_valid_dates:
            missing_info_diagnosis.append(
                "No valid date column was detected. Temporal trend analysis will be limited to row index order."
            )
        if not schema['category']:
            missing_info_diagnosis.append(
                "No categorical department or category column was identified. Data will be aggregated under 'General'."
            )

        self.quality_report = {
            'initial_rows': initial_row_count,
            'cleaned_rows': total_rows_cleaned,
            'duplicates_removed': duplicates_count,
            'missing_cells': missing_cells,
            'missing_rate_pct': round(missing_rate * 100, 2),
            'outlier_count': outlier_count,
            'has_financial_data': has_financial_data,
            'has_valid_dates': has_valid_dates,
            'quality_score': quality_score,
            'diagnostics': missing_info_diagnosis,
            'columns_detected': {k: v for k, v in schema.items() if v is not None}
        }

        self.cleaned_df = df
        return df, self.quality_report

    def get_summary_stats(self):
        """Get quick descriptive statistics of numerical columns."""
        if self.cleaned_df is None:
            return {}
        
        stats = {}
        for col in ['__revenue', '__expense', '__profit']:
            if col in self.cleaned_df.columns:
                s = self.cleaned_df[col]
                stats[col.replace('__', '')] = {
                    'total': float(s.sum()),
                    'mean': float(s.mean()),
                    'median': float(s.median()),
                    'min': float(s.min()),
                    'max': float(s.max()),
                    'std': float(s.std()) if len(s) > 1 else 0.0,
                    'count': int(s.count())
                }
        return stats
