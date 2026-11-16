"""
Unit test suite for analytics and AI engine
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_generator import generate_financials_data, generate_transactions_data, generate_portfolio_data
from src.analytics import calculate_kpis, detect_anomalies, calculate_portfolio_metrics, run_monte_carlo_forecast
from src.ai_engine import FinancialAIEngine

class TestFinanceEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df_fin = generate_financials_data(seed=12)
        cls.df_tx = generate_transactions_data(seed=12)
        cls.df_port = generate_portfolio_data()

    def test_kpi_calculation(self):
        kpis = calculate_kpis(self.df_fin)
        self.assertIn("Total_Revenue", kpis)
        self.assertIn("Gross_Margin_Pct", kpis)
        self.assertIn("EBITDA", kpis)
        self.assertIn("Net_Income", kpis)
        self.assertIn("Runway_Months", kpis)
        self.assertGreater(kpis["Total_Revenue"], 0)
        self.assertGreater(kpis["Gross_Margin_Pct"], 50.0)

    def test_portfolio_metrics(self):
        metrics = calculate_portfolio_metrics(self.df_port)
        self.assertIn("Sharpe_Ratio", metrics)
        self.assertIn("VaR_95_Pct", metrics)
        self.assertIn("Total_Portfolio_Value_M", metrics)
        self.assertGreater(metrics["Total_Portfolio_Value_M"], 0)
        self.assertGreater(metrics["Weighted_Return_Pct"], 0)

    def test_monte_carlo(self):
        summary_df, samples_df = run_monte_carlo_forecast(initial_val=1000000, n_months=12, n_simulations=100)
        self.assertEqual(len(summary_df), 13)
        self.assertIn("P50_Median", summary_df.columns)
        self.assertIn("P10_Bearish", summary_df.columns)

    def test_ai_engine(self):
        kpis = calculate_kpis(self.df_fin)
        engine = FinancialAIEngine(self.df_fin, self.df_tx, self.df_port)
        
        # Test executive brief
        report_md, score, status, color = engine.generate_executive_brief(kpis)
        self.assertTrue(len(report_md) > 200)
        self.assertTrue(0 <= score <= 100)
        
        # Test natural language queries
        ans_cash = engine.answer_query("What is our cash runway?", kpis)
        self.assertIn("Runway", ans_cash)
        
        ans_rev = engine.answer_query("Summarize revenue growth", kpis)
        self.assertIn("Revenue", ans_rev)
        
        # Test audit scanner
        anomalies, stats = engine.audit_transactions()
        self.assertGreater(stats["Total_Transactions"], 0)
        self.assertIn("Flagged_Count", stats)

        # Test stress test scenario
        sim = engine.simulate_scenario(kpis, rev_change_pct=-10, opex_change_pct=5, cogs_change_pct=5)
        self.assertIn("Simulated_Revenue", sim)
        self.assertLess(sim["Simulated_Revenue"], kpis["Total_Revenue"])

if __name__ == "__main__":
    unittest.main()
