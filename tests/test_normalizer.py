import unittest
import io
import pandas as pd
from src.data_normalizer import load_and_normalize_csv, clean_number
from src.analytics import calculate_kpis

class TestNormalizer(unittest.TestCase):
    def test_clean_number(self):
        self.assertEqual(clean_number("$12,500.50"), 12500.50)
        self.assertEqual(clean_number("(4,200.00)"), -4200.00)
        self.assertEqual(clean_number(" -150 "), -150.0)
        self.assertEqual(clean_number("45.2%"), 45.2)
        self.assertEqual(clean_number(""), 0.0)
        self.assertEqual(clean_number(None), 0.0)

    def test_minimal_csv(self):
        csv_data = "Date,Amount\n2025-01-01,100000\n2025-02-01,120000\n"
        df_fin, df_tx, info, ok, msg = load_and_normalize_csv(io.StringIO(csv_data))
        self.assertTrue(ok)
        self.assertEqual(len(df_fin), 2)
        self.assertEqual(df_fin["Revenue"].sum(), 220000)
        self.assertIn("Year", df_fin.columns)
        self.assertIn("Segment", df_fin.columns)
        kpis = calculate_kpis(df_fin)
        self.assertEqual(kpis["Total_Revenue"], 220000)

    def test_arbitrary_columns_csv(self):
        csv_data = (
            'Invoice Date,Client / Customer,Location,Total Invoiced,Direct Spend\n'
            '2025-03-01,Alpha Corp,US East,"$50,000.00","$15,000.00"\n'
            '2025-03-15,Beta Labs,Europe,"$80,000.00","$25,000.00"\n'
        )
        df_fin, df_tx, info, ok, msg = load_and_normalize_csv(io.StringIO(csv_data))
        self.assertTrue(ok)
        self.assertEqual(len(df_fin), 2)
        self.assertEqual(df_fin["Revenue"].sum(), 130000)
        self.assertEqual(df_fin["COGS"].sum(), 40000)
        self.assertEqual(df_fin["Gross_Profit"].sum(), 90000)
        kpis = calculate_kpis(df_fin)
        self.assertEqual(kpis["Total_Revenue"], 130000)
        self.assertEqual(kpis["Gross_Profit"], 90000)

if __name__ == "__main__":
    unittest.main()
