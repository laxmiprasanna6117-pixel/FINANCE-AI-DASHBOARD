import os
import io
from flask import Flask, render_template, request, jsonify, send_file, session
from flask.json.provider import DefaultJSONProvider
import pandas as pd
import numpy as np

from src.data_processor import DataProcessor
from src.financial_kpis import FinancialKPIEngine
from src.ai_engine import FinancialAIEngine
from src.report_generator import FinancialReportGenerator
from src.auth_manager import AuthManager

class CustomJSONProvider(DefaultJSONProvider):
    """Handles serialization of NumPy types, pandas types, and NaNs cleanly."""
    def default(self, obj):
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if pd.isna(obj):
            return None
        return super().default(obj)

app = Flask(__name__)
app.json = CustomJSONProvider(app)
app.config['SECRET_KEY'] = 'fda-financial-ai-dashboard-secret-2026'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload

# In-memory storage for active dataset
active_session = {
    'processor': None,
    'raw_df': None,
    'cleaned_df': None,
    'quality_report': None,
    'filename': None,
    'currency_symbol': '$'
}

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'data', 'samples')

def load_dataset_into_memory(file_or_path, filename):
    """Processes and caches a dataset in the active session."""
    processor = DataProcessor()
    df = processor.load_file(file_or_path, filename=filename)
    cleaned_df, quality = processor.process_and_clean(df)
    
    active_session['processor'] = processor
    active_session['raw_df'] = df
    active_session['cleaned_df'] = cleaned_df
    active_session['quality_report'] = quality
    active_session['filename'] = filename
    return cleaned_df, quality

auth_manager = AuthManager()

@app.route('/')
def index():
    return render_template('index.html')

# =========================================================================
# AUTHENTICATION ROUTES
# =========================================================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    payload = request.get_json(silent=True) or {}
    username = payload.get('username')
    password = payload.get('password')
    full_name = payload.get('full_name')

    success, message, user = auth_manager.register_user(username, password, full_name)
    if not success:
        return jsonify({'success': False, 'error': message}), 400

    session['user_id'] = user['id']
    session['username'] = user['username']
    return jsonify({
        'success': True,
        'message': message,
        'user': user
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    payload = request.get_json(silent=True) or {}
    username = payload.get('username')
    password = payload.get('password')

    success, message, user = auth_manager.verify_user(username, password)
    if not success:
        return jsonify({'success': False, 'error': message}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    return jsonify({
        'success': True,
        'message': message,
        'user': user
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False, 'user': None})

    user = auth_manager.get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'authenticated': False, 'user': None})

    return jsonify({
        'authenticated': True,
        'user': user
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@app.route('/api/status', methods=['GET'])
def get_status():
    has_data = active_session['cleaned_df'] is not None and not active_session['cleaned_df'].empty
    return jsonify({
        'has_data': has_data,
        'filename': active_session['filename'],
        'records_count': len(active_session['cleaned_df']) if has_data else 0,
        'quality_report': active_session['quality_report'],
        'currency_symbol': active_session['currency_symbol']
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part in the request.'}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'success': False, 'error': 'No file selected.'}), 400

    filename = file.filename
    lower_name = filename.lower()
    if not (lower_name.endswith('.csv') or lower_name.endswith(('.xlsx', '.xls'))):
        return jsonify({'success': False, 'error': 'Unsupported file format. Please upload a CSV or Excel (.xlsx, .xls) file.'}), 400

    try:
        cleaned_df, quality = load_dataset_into_memory(file, filename)
        return jsonify({
            'success': True,
            'filename': filename,
            'records_count': len(cleaned_df),
            'quality_report': quality,
            'has_financial_data': quality['has_financial_data']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to process file: {str(e)}'}), 500

@app.route('/api/load-sample', methods=['POST'])
def load_sample():
    sample_key = request.json.get('sample', 'pnl') if request.is_json else 'pnl'

    sample_files = {
        'pnl': ('enterprise_pnl_monthly.csv', 'Enterprise Monthly P&L'),
        'ledger': ('transactions_ledger.csv', 'Daily Transaction Ledger'),
        'budget': ('corporate_budget_actuals.xlsx', 'Corporate Budget vs Actuals (Excel)')
    }

    if sample_key not in sample_files:
        return jsonify({'success': False, 'error': 'Invalid sample selected.'}), 400

    file_name, desc = sample_files[sample_key]
    file_path = os.path.join(SAMPLES_DIR, file_name)

    if not os.path.exists(file_path):
        return jsonify({'success': False, 'error': f'Sample file not found at {file_path}.'}), 404

    try:
        cleaned_df, quality = load_dataset_into_memory(file_path, file_name)
        return jsonify({
            'success': True,
            'filename': f"{file_name} ({desc})",
            'records_count': len(cleaned_df),
            'quality_report': quality
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to load sample: {str(e)}'}), 500

@app.route('/api/dashboard-data', methods=['POST'])
def get_dashboard_data():
    if active_session['cleaned_df'] is None or active_session['cleaned_df'].empty:
        return jsonify({'success': False, 'error': 'No active dataset loaded.'}), 400

    payload = request.get_json(silent=True) or {}
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    category = payload.get('category')
    frequency = payload.get('frequency', 'monthly')
    search = payload.get('search')
    page = int(payload.get('page', 1))
    page_size = int(payload.get('page_size', 20))

    cleaned_df = active_session['cleaned_df']
    kpi_engine = FinancialKPIEngine(cleaned_df, active_session['quality_report'])

    filtered_df = kpi_engine.filter_data(
        start_date=start_date,
        end_date=end_date,
        category=category,
        search=search
    )

    kpis = kpi_engine.calculate_kpis(filtered_df)
    time_series = kpi_engine.get_time_series_data(filtered_df, frequency=frequency)
    categories = kpi_engine.get_category_breakdown(filtered_df)
    budget_vs_actual = kpi_engine.get_budget_vs_actual(filtered_df)
    payment_status = kpi_engine.get_payment_status_breakdown(filtered_df)
    filter_options = kpi_engine.get_filter_options()

    # Paginated data table rows
    display_cols = [c for c in filtered_df.columns if not c.startswith('__')]
    for col_req in ['__revenue', '__expense', '__profit', '__category']:
        if col_req in filtered_df.columns and col_req not in display_cols:
            display_cols.append(col_req)

    total_filtered_rows = len(filtered_df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    sliced_df = filtered_df[display_cols].iloc[start_idx:end_idx]
    
    # Format table data
    table_headers = [c.replace('__', '').title() for c in display_cols]
    table_rows = []
    for row in sliced_df.itertuples(index=False):
        formatted_row = []
        for val in row:
            if pd.isna(val):
                formatted_row.append("-")
            elif isinstance(val, (int, float)):
                formatted_row.append(f"{val:,.2f}")
            else:
                formatted_row.append(str(val))
        table_rows.append(formatted_row)

    return jsonify({
        'success': True,
        'kpis': kpis,
        'time_series': time_series,
        'categories': categories,
        'budget_vs_actual': budget_vs_actual,
        'payment_status': payment_status,
        'filter_options': filter_options,
        'table': {
            'headers': table_headers,
            'rows': table_rows,
            'total_rows': total_filtered_rows,
            'page': page,
            'page_size': page_size,
            'total_pages': max(1, (total_filtered_rows + page_size - 1) // page_size)
        }
    })

@app.route('/api/ai-insights', methods=['POST'])
def get_ai_insights():
    if active_session['cleaned_df'] is None or active_session['cleaned_df'].empty:
        return jsonify({'success': False, 'error': 'No active dataset loaded.'}), 400

    payload = request.get_json(silent=True) or {}
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    category = payload.get('category')

    cleaned_df = active_session['cleaned_df']
    kpi_engine = FinancialKPIEngine(cleaned_df, active_session['quality_report'])
    filtered_df = kpi_engine.filter_data(start_date=start_date, end_date=end_date, category=category)

    kpis = kpi_engine.calculate_kpis(filtered_df)
    time_series = kpi_engine.get_time_series_data(filtered_df, frequency='monthly')
    categories = kpi_engine.get_category_breakdown(filtered_df)

    ai_engine = FinancialAIEngine(filtered_df, kpis, time_series, categories)
    insights = ai_engine.run_full_analysis()

    return jsonify({
        'success': True,
        'insights': insights
    })

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    if active_session['cleaned_df'] is None or active_session['cleaned_df'].empty:
        return "No active dataset loaded to export.", 400

    df = active_session['cleaned_df']
    quality = active_session['quality_report']
    kpi_engine = FinancialKPIEngine(df, quality)
    kpis = kpi_engine.calculate_kpis(df)
    ts = kpi_engine.get_time_series_data(df, 'monthly')
    cats = kpi_engine.get_category_breakdown(df)

    ai = FinancialAIEngine(df, kpis, ts, cats)
    insights = ai.run_full_analysis()

    generator = FinancialReportGenerator(df, kpis, insights, quality, ts, cats)
    pdf_buffer = generator.generate_pdf()

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='Financial_Intelligence_Report.pdf'
    )

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    if active_session['cleaned_df'] is None or active_session['cleaned_df'].empty:
        return "No active dataset loaded to export.", 400

    df = active_session['cleaned_df']
    quality = active_session['quality_report']
    kpi_engine = FinancialKPIEngine(df, quality)
    kpis = kpi_engine.calculate_kpis(df)
    ts = kpi_engine.get_time_series_data(df, 'monthly')
    cats = kpi_engine.get_category_breakdown(df)

    ai = FinancialAIEngine(df, kpis, ts, cats)
    insights = ai.run_full_analysis()

    generator = FinancialReportGenerator(df, kpis, insights, quality, ts, cats)
    excel_buffer = generator.generate_excel()

    return send_file(
        excel_buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Financial_Analytics_Model.xlsx'
    )

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    if active_session['cleaned_df'] is None or active_session['cleaned_df'].empty:
        return "No active dataset loaded to export.", 400

    df = active_session['cleaned_df'].copy()
    display_cols = [c for c in df.columns if not c.startswith('__')]
    for sc in ['__revenue', '__expense', '__profit', '__category']:
        if sc in df.columns and sc not in display_cols:
            display_cols.append(sc)

    buf = io.StringIO()
    df[display_cols].to_csv(buf, index=False)
    mem_buf = io.BytesIO(buf.getvalue().encode('utf-8'))

    return send_file(
        mem_buf,
        mimetype='text/csv',
        as_attachment=True,
        download_name='Cleaned_Financial_Data.csv'
    )

@app.route('/api/reset', methods=['POST'])
def reset_dataset():
    active_session['processor'] = None
    active_session['raw_df'] = None
    active_session['cleaned_df'] = None
    active_session['quality_report'] = None
    active_session['filename'] = None
    return jsonify({'success': True, 'message': 'Dataset reset successfully.'})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    payload = request.get_json(silent=True) or {}
    curr = payload.get('currency', '$')
    active_session['currency_symbol'] = curr
    return jsonify({'success': True, 'currency_symbol': curr})

# Auto-load the P&L sample on module init so users immediately see a working system
pnl_sample = os.path.join(SAMPLES_DIR, 'enterprise_pnl_monthly.csv')
if os.path.exists(pnl_sample):
    try:
        load_dataset_into_memory(pnl_sample, 'enterprise_pnl_monthly.csv')
        print(f"Loaded baseline dataset: enterprise_pnl_monthly.csv ({len(active_session['cleaned_df'])} rows)", flush=True)
    except Exception as e:
        print(f"Could not preload sample: {e}", flush=True)

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    print("=================================================================", flush=True)
    print("Finance Data Analysis & AI Automation Dashboard is ready!", flush=True)
    try:
        from waitress import serve
        print(f"Serving production WSGI via Waitress on http://{host}:{port}", flush=True)
        print("=================================================================", flush=True)
        serve(app, host=host, port=port, threads=6)
    except ImportError:
        print(f"Serving on http://{host}:{port}", flush=True)
        print("=================================================================", flush=True)
        app.run(host=host, port=port, debug=False)
