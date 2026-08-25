import unittest
import pandas as pd
import numpy as np
import io
from src.visualization.recommender import recommend_chart
from src.analytics.insights import generate_data_insights
from src.export.exporters import to_excel, to_csv

class TestPhase6DataIntelligence(unittest.TestCase):
    def setUp(self):
        # Create a mock DataFrame representing sales data
        self.df_sales = pd.DataFrame({
            "Date": pd.date_range(start="2026-01-01", periods=10, freq="D"),
            "Category": ["Electronics", "Electronics", "Furniture", "Furniture", "Office", "Office", "Electronics", "Furniture", "Office", "Electronics"],
            "Sales": [1200.50, 1500.00, 800.25, 950.00, 150.75, 300.00, 1100.00, 850.50, 450.00, 2000.00],
            "Quantity": [2, 3, 1, 2, 5, 10, 2, 2, 4, 5],
            "Region": ["North", "South", "North", "East", "West", "East", "South", "North", "West", "North"]
        })

        # DataFrame with high missing values
        self.df_missing = pd.DataFrame({
            "A": [1, 2, np.nan, 4, 5],
            "B": ["X", np.nan, "Y", "Z", np.nan]
        })

    def test_visualization_recommender_trend(self):
        """Should recommend a Line Chart if a Datetime index or Date column exists with numeric columns."""
        config = recommend_chart(self.df_sales)
        self.assertIsNotNone(config)
        self.assertEqual(config.chart_type, "line")
        self.assertEqual(config.x_axis, "Date")
        self.assertEqual(config.y_axis, "Sales")

    def test_visualization_recommender_category(self):
        """Should recommend a Bar Chart if category/object column and a numeric column exists without date trend."""
        df_cat = self.df_sales.drop(columns=["Date"])
        config = recommend_chart(df_cat)
        self.assertIsNotNone(config)
        self.assertIn(config.chart_type, ["bar", "pie"])
        self.assertEqual(config.x_axis, "Category")
        self.assertEqual(config.y_axis, "Sales")

    def test_visualization_recommender_histogram(self):
        """Should recommend a Histogram or Box plot for single numeric column datasets."""
        df_single_numeric = pd.DataFrame({"A": [1, 2, 1, 3, 2, 4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9]})
        config = recommend_chart(df_single_numeric)
        self.assertIsNotNone(config)
        self.assertEqual(config.chart_type, "histogram")

    def test_analytics_insights_sales(self):
        """Should generate mathematical/statistical insights for numerical columns."""
        insights = generate_data_insights(self.df_sales)
        self.assertTrue(len(insights) > 0)
        
        # Check if min/max/mean mentions are present in the list
        has_sales_stats = any("Sales" in insight for insight in insights)
        self.assertTrue(has_sales_stats, "Should calculate insights for 'Sales'")

    def test_analytics_insights_missing_data(self):
        """Should detect missing data rates and flag columns correctly."""
        insights = generate_data_insights(self.df_missing)
        has_missing_notice = any("missing" in insight.lower() or "null" in insight.lower() for insight in insights)
        self.assertTrue(has_missing_notice, "Should notice and list missing values statistics")

    def test_styled_excel_exporter(self):
        """Should execute OpenPyXL rendering without errors and generate valid xlsx workbook bytes."""
        xlsx_bytes = to_excel(self.df_sales)
        self.assertIsInstance(xlsx_bytes, bytes)
        self.assertTrue(len(xlsx_bytes) > 0)
        
        # Verify xlsx signature
        self.assertTrue(xlsx_bytes.startswith(b"PK"), "Should be a valid ZIP archive (XLSX signature)")

if __name__ == "__main__":
    unittest.main()
