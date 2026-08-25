import unittest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.ai.schemas import StructuredOperation, FilterCondition, SortCondition, AggregateOperation, AIResponse
from src.ai.gemini_client import build_relevance_context, query_gemini_intelligence
from src.execution.code_renderer import render_pandas_code
from src.state import SessionStateManager

class TestAIEngine(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame
        self.df = pd.DataFrame({
            "Product": ["Apple", "Banana", "Cherry", "Date"],
            "Revenue": [100.5, 200.0, 150.75, 300.25],
            "Quantity": [10, 20, 15, 30],
            "Region": ["North", "South", "North", "West"]
        })
        # Set up Streamlit-like session state
        import streamlit as st
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        SessionStateManager.init_state()
        SessionStateManager.set_current_df(self.df)

    def test_build_relevance_context_with_specific_columns(self):
        # Query mentioning Revenue
        ctx = build_relevance_context(self.df, "Show columns like Revenue and Product")
        self.assertEqual(ctx["total_rows"], 4)
        self.assertEqual(ctx["total_cols"], 4)
        # Revenue and Product should have RELEVANT tag in their description
        self.assertIn("Revenue", ctx["column_details_str"])
        self.assertIn("RELEVANT", ctx["column_details_str"])
        self.assertIn("Revenue", ctx["sample_rows_str"])
        self.assertIn("Product", ctx["sample_rows_str"])

    def test_build_relevance_context_no_match_fallback(self):
        # Query with no column name match
        ctx = build_relevance_context(self.df, "Clean the data please")
        self.assertEqual(ctx["total_rows"], 4)
        self.assertEqual(ctx["total_cols"], 4)
        # All columns should be treated as fallback/relevant
        for col in ["Product", "Revenue", "Quantity", "Region"]:
            self.assertIn(col, ctx["column_details_str"])

    def test_render_pandas_code_filters_and_sorts(self):
        op = StructuredOperation(
            intent="filter_sort",
            filters=[
                FilterCondition(column="Revenue", operator=">", value=150.0),
                FilterCondition(column="Region", operator="==", value="North")
            ],
            sort=[
                SortCondition(column="Quantity", ascending=False)
            ],
            limit=5,
            explanation="Filter high revenue in North and sort by quantity desc."
        )
        code = render_pandas_code(op)
        self.assertIn("result = df.copy()", code)
        self.assertIn("result = result[result['Revenue'] > 150.0]", code)
        self.assertIn("result = result[result['Region'] == 'North']", code)
        self.assertIn("result = result.sort_values(by=['Quantity'], ascending=[False])", code)
        self.assertIn("result = result.head(5)", code)

    def test_render_pandas_code_aggregations(self):
        op = StructuredOperation(
            intent="aggregate",
            group_by=["Region"],
            aggregations=[
                AggregateOperation(column="Revenue", func="sum", alias="Total Revenue"),
                AggregateOperation(column="Quantity", func="mean", alias="Avg Quantity")
            ],
            explanation="Sum revenue and average quantity grouped by Region."
        )
        code = render_pandas_code(op)
        self.assertIn("groupby(['Region'])", code)
        self.assertIn("Total Revenue=pd.NamedAgg(column='Revenue', aggfunc='sum')", code)
        self.assertIn("Avg Quantity=pd.NamedAgg(column='Quantity', aggfunc='mean')", code)

    def test_query_gemini_intelligence_client_missing(self):
        # Force client to be None (no API key configured)
        with patch("src.ai.gemini_client.get_gemini_client", return_value=None):
            resp = query_gemini_intelligence("Show top 5 records")
            self.assertEqual(resp.status, "ai_error")
            self.assertIn("Gemini Client is unavailable", resp.error)
            self.assertGreater(SessionStateManager.get_ai_request_count(), 0)
            self.assertEqual(SessionStateManager.get_ai_request_status(), "Failed (No Client)")

    def test_client_initialization_with_api_key(self):
        # Test A: Gemini client initializes with GEMINI_API_KEY
        with patch("src.ai.gemini_client.get_gemini_api_key", return_value="fake-api-key"):
            with patch("google.genai.Client") as mock_client_cls:
                from src.ai.gemini_client import get_gemini_client
                client = get_gemini_client()
                mock_client_cls.assert_called_once_with(api_key="fake-api-key")
                self.assertIsNotNone(client)

    def test_sanitize_gemini_schema_removes_additional_properties(self):
        # Test F: Verifies no additionalProperties exists in the sanitized schema
        from src.ai.gemini_client import sanitize_gemini_schema
        sanitized = sanitize_gemini_schema(AIResponse)
        
        # Verify recursively that additionalProperties/additional_properties are removed
        def check_no_additional_properties(node):
            if isinstance(node, dict):
                self.assertNotIn("additionalProperties", node)
                self.assertNotIn("additional_properties", node)
                for v in node.values():
                    check_no_additional_properties(v)
            elif isinstance(node, list):
                for item in node:
                    check_no_additional_properties(item)
                    
        check_no_additional_properties(sanitized)

    def test_invalid_operations_rejected(self):
        # Test E: Invalid operations are rejected by the safety layer
        from src.execution.safety import validate_operation
        # Non-existent column
        op = StructuredOperation(
            intent="filter_sort",
            filters=[FilterCondition(column="NonExistentCol", operator="==", value=10)],
            explanation="Invalid filter"
        )
        res = validate_operation(op, self.df)
        self.assertFalse(res["valid"])
        self.assertTrue(any("does not exist" in err or "non-existent" in err for err in res["errors"]))

    def test_live_gemini_request_and_structured_output(self):
        # Tests B, C, D, F: Normal request reaches Gemini, structured output is returned,
        # validates against StructuredOperation, no additionalProperties error occurs.
        from src.config import IS_GEMINI_AVAILABLE
        if not IS_GEMINI_AVAILABLE:
            self.skipTest("Real Gemini API Key not configured/available.")
            
        # Run a real natural language request
        resp = query_gemini_intelligence("Show the top 10 records by revenue.")
        
        # Verify status is success or validation error (if dataset columns don't match, etc.)
        self.assertNotEqual(resp.status, "ai_error", f"Request failed: {resp.error}")
        self.assertEqual(resp.status, "success")
        self.assertIsNotNone(resp.operation)
        self.assertEqual(resp.operation.intent, "filter_sort")
        self.assertEqual(resp.operation.limit, 10)
        
        # Verify sort is correct
        self.assertIsNotNone(resp.operation.sort)
        self.assertEqual(resp.operation.sort[0].column, "Revenue")
        self.assertEqual(resp.operation.sort[0].ascending, False)

if __name__ == "__main__":
    unittest.main()

