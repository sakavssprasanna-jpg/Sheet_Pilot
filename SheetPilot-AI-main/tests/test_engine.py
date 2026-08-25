import unittest
import pandas as pd
import numpy as np
import os
from io import BytesIO

from src.data.loader import load_file
from src.data.profiler import profile_dataframe
from src.data.context import generate_dataset_context
from src.execution.safety import validate_operation
from src.execution.operation_engine import execute_operation
from src.ai.schemas import StructuredOperation, FilterCondition, SortCondition, AggregateOperation, ColumnTransformation

class TestDataIntelligenceEngine(unittest.TestCase):
    
    def setUp(self):
        # Create a tiny test dataframe
        self.data = pd.DataFrame({
            "EmployeeID": [101, 102, 103, 104, 105],
            "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "Department": ["Sales", "Sales", "Engineering", "Engineering", "Marketing"],
            "Salary": [75000, 95000, 110000, 85000, 60000],
            "Commission_Pct": ["10%", "15%", "0%", "5%", "20%"],
            "Sales_USD": ["$12,000", "$45,000", "$0", "$8,000", "$15,000"]
        })
        # Save as temporary CSV string
        self.csv_bytes = BytesIO(self.data.to_csv(index=False).encode('utf-8'))
        self.csv_bytes.name = "test_data.csv"

    def test_loader_valid(self):
        df, err = load_file(self.csv_bytes, "test_data.csv")
        self.assertNilOrNone(err)
        self.assertEqual(df.shape, (5, 6))

    def test_loader_empty_file(self):
        empty_bytes = BytesIO(b"")
        empty_bytes.name = "empty.csv"
        df, err = load_file(empty_bytes, "empty.csv")
        self.assertIsNotNone(err)
        self.assertIn("empty", err.lower())

    def test_loader_duplicate_columns(self):
        dup_bytes = BytesIO(b"ColA,ColA,ColB\n1,2,3\n")
        dup_bytes.name = "dup.csv"
        df, err = load_file(dup_bytes, "dup.csv")
        self.assertIsNotNone(err)
        self.assertIn("duplicate", err.lower())

    def test_profiler_statistics(self):
        profile = profile_dataframe(self.data)
        self.assertEqual(profile["shape"]["rows"], 5)
        self.assertEqual(profile["shape"]["cols"], 6)
        self.assertEqual(profile["duplicate_rows"], 0)
        self.assertEqual(profile["total_missing_cells"], 0)
        
        # Check inferred semantic types
        cols_meta = {c["name"]: c["semantic_type"] for c in profile["columns"]}
        self.assertEqual(cols_meta["EmployeeID"], "identifier")
        self.assertEqual(cols_meta["Department"], "categorical")
        self.assertEqual(cols_meta["Salary"], "currency-like") # Salary matches price/salary revenue keyword
        self.assertEqual(cols_meta["Commission_Pct"], "percentage-like") # Ends with %
        self.assertEqual(cols_meta["Sales_USD"], "currency-like") # Starts with $

    def test_context_generation(self):
        profile = profile_dataframe(self.data)
        context = generate_dataset_context(profile, "test_data.csv")
        self.assertIn("test_data.csv", context)
        self.assertIn("EmployeeID** (int64 / identifier)", context)
        self.assertIn("Sample Data", context)

    def test_filter_operation_positive(self):
        # Filter: Salary > 80000
        op = StructuredOperation(
            intent="filter_sort",
            filters=[
                FilterCondition(column="Salary", operator=">", value=80000)
            ],
            explanation="Filter for salaries greater than 80000"
        )
        res = execute_operation(op, self.data)
        self.assertTrue(res.success)
        self.assertEqual(res.rows_after, 3) # Bob (95000), Charlie (110000), David (85000)
        self.assertNilOrNone(res.result_dataframe.index.name)

    def test_filter_value_cast_compatibility(self):
        # Filter: Salary > "80000" (string input for integer column)
        op = StructuredOperation(
            intent="filter_sort",
            filters=[
                FilterCondition(column="Salary", operator=">", value="80000")
            ],
            explanation="Filter with string value"
        )
        res = execute_operation(op, self.data)
        self.assertTrue(res.success)
        self.assertEqual(res.rows_after, 3)

    def test_sorting_operation(self):
        # Sort by Salary descending
        op = StructuredOperation(
            intent="filter_sort",
            sort=[
                SortCondition(column="Salary", ascending=False)
            ],
            explanation="Sort by Salary descending"
        )
        res = execute_operation(op, self.data)
        self.assertTrue(res.success)
        # Verify first row has highest salary
        first_salary = res.result_dataframe.iloc[0]["Salary"]
        self.assertEqual(first_salary, 110000)

    def test_groupby_aggregation(self):
        # Group by Department, calculate Salary mean
        op = StructuredOperation(
            intent="aggregate",
            group_by=["Department"],
            aggregations=[
                AggregateOperation(column="Salary", func="mean", alias="Avg_Salary")
            ],
            explanation="Group by department and get average salary"
        )
        res = execute_operation(op, self.data)
        self.assertTrue(res.success)
        self.assertEqual(res.columns_after, 2)
        sales_avg = res.result_dataframe[res_df_dep_mask(res.result_dataframe, "Sales")]["Avg_Salary"].values[0]
        self.assertEqual(sales_avg, 85000.0) # (75000 + 95000) / 2

    def test_limit_operation(self):
        # Top 2 rows
        op = StructuredOperation(
            intent="filter_sort",
            limit=2,
            explanation="Limit top 2"
        )
        res = execute_operation(op, self.data)
        self.assertTrue(res.success)
        self.assertEqual(res.rows_after, 2)

    def test_invalid_column_validation(self):
        # Column 'Nonexistent' does not exist
        op = StructuredOperation(
            intent="filter_sort",
            filters=[
                FilterCondition(column="Nonexistent", operator="==", value="test")
            ],
            explanation="Invalid column test"
        )
        res = execute_operation(op, self.data)
        self.assertFalse(res.success)
        self.assertIn("Nonexistent", res.operation_summary)

    def test_empty_results_handling(self):
        # Filter that returns nothing
        op = StructuredOperation(
            intent="filter_sort",
            filters=[
                FilterCondition(column="Salary", operator=">", value=1000000)
            ],
            explanation="Filter yielding empty results"
        )
        res = execute_operation(op, self.data)
        self.assertTrue(res.success)
        self.assertEqual(res.rows_after, 0)

    def test_math_transformation_explicit(self):
        # Salary = Salary * 1.1
        op = StructuredOperation(
            intent="transformation",
            transformations=[
                ColumnTransformation(
                    column="Salary",
                    new_column="New_Salary",
                    operation="math",
                    args={"operator": "*", "operand": 1.1}
                )
            ],
            explanation="Increment Salary by 10%"
        )
        res = execute_operation(op, self.data)
        self.assertTrue(res.success)
        self.assertEqual(res.result_dataframe.iloc[0]["New_Salary"], 75000 * 1.1)

    def assertNilOrNone(self, value):
        self.assertTrue(value is None or value == "")

def res_df_dep_mask(df, val):
    return df["Department"] == val

if __name__ == '__main__':
    unittest.main()
