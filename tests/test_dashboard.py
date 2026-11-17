import unittest
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processor import DataProcessor
from src.financial_kpis import FinancialKPIEngine
from src.ai_engine import FinancialAIEngine
from src.report_generator import FinancialReportGenerator
from app import app

class TestFinancialDashboard(unittest.TestCase):

    def setUp(self):
        self.sample_pnl = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'samples', 'enterprise_pnl_monthly.csv'))
        self.sample_excel = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'samples', 'corporate_budget_actuals.xlsx'))
        self.sample_ledger = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'samples', 'transactions_ledger.csv'))

    def test_pnl_processing(self):
        p = DataProcessor()
        df = p.load_file(self.sample_pnl)
        cleaned, quality = p.process_and_clean(df)
        self.assertTrue(quality['has_financial_data'])
        self.assertGreater(quality['quality_score'], 80)
        self.assertIn('revenue', quality['columns_detected'])
        self.assertIn('expense', quality['columns_detected'])

    def test_kpi_engine(self):
        p = DataProcessor()
        df = p.load_file(self.sample_pnl)
        cleaned, quality = p.process_and_clean(df)
        engine = FinancialKPIEngine(cleaned, quality)
        kpis = engine.calculate_kpis(cleaned)
        self.assertGreater(kpis['total_revenue'], 0)
        self.assertGreater(kpis['total_expenses'], 0)
        self.assertEqual(kpis['total_transactions'], 144)

    def test_ai_insights_engine(self):
        p = DataProcessor()
        df = p.load_file(self.sample_pnl)
        cleaned, quality = p.process_and_clean(df)
        engine = FinancialKPIEngine(cleaned, quality)
        kpis = engine.calculate_kpis(cleaned)
        ts = engine.get_time_series_data(cleaned, 'monthly')
        cats = engine.get_category_breakdown(cleaned)
        
        ai = FinancialAIEngine(cleaned, kpis, ts, cats)
        insights = ai.run_full_analysis()
        self.assertIn('anomalies', insights)
        self.assertIn('risks', insights)
        self.assertIn('recommendations', insights)
        self.assertGreater(len(insights['executive_summary']), 50)

    def test_report_generation(self):
        p = DataProcessor()
        df = p.load_file(self.sample_pnl)
        cleaned, quality = p.process_and_clean(df)
        engine = FinancialKPIEngine(cleaned, quality)
        kpis = engine.calculate_kpis(cleaned)
        ts = engine.get_time_series_data(cleaned, 'monthly')
        cats = engine.get_category_breakdown(cleaned)
        ai = FinancialAIEngine(cleaned, kpis, ts, cats)
        insights = ai.run_full_analysis()

        rep = FinancialReportGenerator(cleaned, kpis, insights, quality, ts, cats)
        pdf = rep.generate_pdf()
        excel = rep.generate_excel()
        self.assertGreater(len(pdf.getvalue()), 1000)
        self.assertGreater(len(excel.getvalue()), 1000)

    def test_api_endpoints(self):
        client = app.test_client()
        res = client.get('/api/status')
        self.assertEqual(res.status_code, 200)

        res_dash = client.post('/api/dashboard-data', json={'frequency': 'monthly', 'category': 'all'})
        self.assertEqual(res_dash.status_code, 200)

        res_ai = client.post('/api/ai-insights', json={})
        self.assertEqual(res_ai.status_code, 200)

    def test_authentication(self):
        client = app.test_client()
        # Verify default admin
        res_login = client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
        self.assertEqual(res_login.status_code, 200)
        self.assertTrue(res_login.get_json()['success'])

        # Verify me
        res_me = client.get('/api/auth/me')
        self.assertTrue(res_me.get_json()['authenticated'])

        # Verify logout
        res_logout = client.post('/api/auth/logout')
        self.assertEqual(res_logout.status_code, 200)
        self.assertFalse(client.get('/api/auth/me').get_json()['authenticated'])

if __name__ == '__main__':
    unittest.main()
