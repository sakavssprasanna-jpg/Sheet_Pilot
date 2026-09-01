import pandas as pd
import numpy as np
import time
from typing import Tuple, Optional, List, Dict, Any
from src.ai.schemas import StructuredOperation
from .safety import validate_operation

class ExecutionResult:
    """Structured execution result containing metadata about the transformation."""
    def __init__(self, 
                 success: bool, 
                 result_dataframe: Optional[pd.DataFrame], 
                 operation_summary: str,
                 rows_before: int, 
                 rows_after: int, 
                 columns_before: int, 
                 columns_after: int,
                 warnings: List[str], 
                 execution_time: float):
        self.success = success
        self.result_dataframe = result_dataframe
        self.operation_summary = operation_summary
        self.rows_before = rows_before
        self.rows_after = rows_after
        self.columns_before = columns_before
        self.columns_after = columns_after
        self.warnings = warnings
        self.execution_time = execution_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "operation_summary": self.operation_summary,
            "rows_before": self.rows_before,
            "rows_after": self.rows_after,
            "columns_before": self.columns_before,
            "columns_after": self.columns_after,
            "warnings": self.warnings,
            "execution_time_seconds": round(self.execution_time, 4)
        }

def safe_cast_value(series: pd.Series, val: Any) -> Any:
    """Convert comparison value to match the column series data type safely."""
    if val is None:
        return None
    try:
        dtype = str(series.dtype)
        if "int" in dtype:
            return int(float(str(val)))
        elif "float" in dtype:
            return float(str(val))
        elif "bool" in dtype:
            return str(val).lower() in ["true", "1", "yes", "y", "t"]
    except Exception:
        pass
    return val

def execute_operation(op: StructuredOperation, df: pd.DataFrame) -> ExecutionResult:
    """
    Executes a structured operation on a Pandas DataFrame using explicit whitelisted pandas mapping.
    This avoids any arbitrary python string evaluation (no eval or exec).
    """
    start_time = time.time()
    
    if df is None:
        return ExecutionResult(
            success=False,
            result_dataframe=None,
            operation_summary="Execution failed: No active dataset.",
            rows_before=0, rows_after=0,
            columns_before=0, columns_after=0,
            warnings=["No dataset provided."],
            execution_time=0.0
        )
        
    rows_before, columns_before = df.shape
    
    # 1. Run Validation
    val_res = validate_operation(op, df)
    if not val_res["valid"]:
        summary = "Validation errors: " + "; ".join(val_res["errors"])
        return ExecutionResult(
            success=False,
            result_dataframe=None,
            operation_summary=summary,
            rows_before=rows_before, rows_after=rows_before,
            columns_before=columns_before, columns_after=columns_before,
            warnings=val_res["warnings"],
            execution_time=time.time() - start_time
        )
        
    try:
        # Create a deep copy to preserve the original unmodified DataFrame
        res_df = df.copy()
        
        # 2. Transformations
        if op.transformations:
            for trans in op.transformations:
                col = trans.column
                new_col = trans.new_column if trans.new_column else col
                
                if trans.operation == "string_upper":
                    res_df[new_col] = res_df[col].astype(str).str.upper()
                elif trans.operation == "string_lower":
                    res_df[new_col] = res_df[col].astype(str).str.lower()
                elif trans.operation == "fill_na":
                    fill_val = trans.args.get("value", "")
                    res_df[new_col] = res_df[col].fillna(fill_val)
                elif trans.operation == "drop_na":
                    res_df = res_df.dropna(subset=[col])
                elif trans.operation == "math":
                    math_op = trans.args.get("operator")
                    operand = trans.args.get("operand")
                    
                    # Convert column values to numeric first for safe math operations
                    col_series = pd.to_numeric(res_df[col], errors="coerce")
                    
                    try:
                        # Case A: Operand is a number constant
                        operand_val = float(str(operand))
                        if math_op == "+":
                            res_df[new_col] = col_series + operand_val
                        elif math_op == "-":
                            res_df[new_col] = col_series - operand_val
                        elif math_op == "*":
                            res_df[new_col] = col_series * operand_val
                        elif math_op == "/":
                            res_df[new_col] = col_series / operand_val
                    except ValueError:
                        # Case B: Operand is another column name
                        operand_col = str(operand)
                        operand_series = pd.to_numeric(res_df[operand_col], errors="coerce")
                        if math_op == "+":
                            res_df[new_col] = col_series + operand_series
                        elif math_op == "-":
                            res_df[new_col] = col_series - operand_series
                        elif math_op == "*":
                            res_df[new_col] = col_series * operand_series
                        elif math_op == "/":
                            res_df[new_col] = col_series / operand_series

        # 3. Filters
        if op.filters:
            for f in op.filters:
                col = f.column
                op_type = f.operator
                val = f.value
                
                safe_val = safe_cast_value(res_df[col], val)
                
                if op_type == "==":
                    res_df = res_df[res_df[col] == safe_val]
                elif op_type == "!=":
                    res_df = res_df[res_df[col] != safe_val]
                elif op_type == ">":
                    res_df = res_df[res_df[col] > safe_val]
                elif op_type == "<":
                    res_df = res_df[res_df[col] < safe_val]
                elif op_type == ">=":
                    res_df = res_df[res_df[col] >= safe_val]
                elif op_type == "<=":
                    res_df = res_df[res_df[col] <= safe_val]
                elif op_type == "contains":
                    res_df = res_df[res_df[col].astype(str).str.contains(str(val), case=False, na=False)]
                elif op_type == "startswith":
                    res_df = res_df[res_df[col].astype(str).str.startswith(str(val), na=False)]
                elif op_type == "endswith":
                    res_df = res_df[res_df[col].astype(str).str.endswith(str(val), na=False)]
                elif op_type == "isnull":
                    res_df = res_df[res_df[col].isnull()]
                elif op_type == "notnull":
                    res_df = res_df[res_df[col].notnull()]

        # 4. Group By & Aggregation
        if op.aggregations:
            if op.group_by:
                agg_mapping = {}
                for agg in op.aggregations:
                    col_name = op.group_by[0] if agg.column == "*" else agg.column
                    func_name = "count" if agg.column == "*" else agg.func
                    agg_mapping[agg.alias] = pd.NamedAgg(column=col_name, aggfunc=func_name)
                    
                res_df = res_df.groupby(op.group_by).agg(**agg_mapping).reset_index()
            else:
                flat_agg_data = {}
                for agg in op.aggregations:
                    col = agg.column
                    func = agg.func
                    alias = agg.alias
                    
                    if col == "*":
                        val = len(res_df)
                    else:
                        series = res_df[col]
                        if func == "sum":
                            val = series.sum()
                        elif func == "mean":
                            val = series.mean()
                        elif func == "median":
                            val = series.median()
                        elif func == "min":
                            val = series.min()
                        elif func == "max":
                            val = series.max()
                        elif func == "std":
                            val = series.std()
                        elif func == "count":
                            val = series.count()
                        elif func == "nunique":
                            val = series.nunique()
                        else:
                            val = None
                            
                    # Cast clean python scalar representation
                    if val is not None and not isinstance(val, (int, float, str, bool)):
                        try:
                            val = float(val)
                        except Exception:
                            val = str(val)
                            
                    flat_agg_data[alias] = [val]
                res_df = pd.DataFrame(flat_agg_data)

        # 5. Sorting
        if op.sort:
            cols = [s.column for s in op.sort]
            ascs = [s.ascending for s in op.sort]
            res_df = res_df.sort_values(by=cols, ascending=ascs)
            
        # 6. Column Selection
        if op.select_columns:
            res_df = res_df[op.select_columns]
            
        # 7. Drop Duplicates (if intent is duplicate_check)
        if op.intent == "duplicate_check":
            res_df = res_df.drop_duplicates()
            
        # 8. Limit
        if op.limit is not None:
            res_df = res_df.head(op.limit)
            
        rows_after, columns_after = res_df.shape
        execution_time = time.time() - start_time
        
        summary = op.explanation if op.explanation else f"Successfully executed intent '{op.intent}'."
        
        return ExecutionResult(
            success=True,
            result_dataframe=res_df,
            operation_summary=summary,
            rows_before=rows_before, rows_after=rows_after,
            columns_before=columns_before, columns_after=columns_after,
            warnings=val_res["warnings"],
            execution_time=execution_time
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            result_dataframe=None,
            operation_summary=f"Execution error occurred: {str(e)}",
            rows_before=rows_before, rows_after=rows_before,
            columns_before=columns_before, columns_after=columns_before,
            warnings=[],
            execution_time=time.time() - start_time
        )
