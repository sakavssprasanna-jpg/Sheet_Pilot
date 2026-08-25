import pandas as pd
import re
from typing import Tuple, List, Dict, Any
from src.ai.schemas import StructuredOperation

ALLOWED_INTENTS = {"profile", "filter_sort", "aggregate", "transformation", "duplicate_check", "missing_check", "chart"}
ALLOWED_OPERATORS = {"==", "!=", ">", "<", ">=", "<=", "contains", "startswith", "endswith", "isnull", "notnull"}
ALLOWED_TRANSFORMATIONS = {"math", "string_upper", "string_lower", "fill_na", "drop_na"}
ALLOWED_AGGS = {"sum", "mean", "median", "min", "max", "count", "nunique", "std"}

def validate_operation(op: StructuredOperation, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the StructuredOperation schema against the active DataFrame dataset.
    Returns a dict containing:
      - valid: bool
      - errors: list of user-friendly error strings
      - warnings: list of minor warning strings
    """
    errors = []
    warnings = []
    
    if df is None:
        errors.append("No active dataset loaded in workspace.")
        return {"valid": False, "errors": errors, "warnings": warnings}
        
    df_cols = set(df.columns.map(str))
    
    # 1. Intent Validation
    if op.intent not in ALLOWED_INTENTS:
        errors.append(f"Operation intent '{op.intent}' is unsupported. Allowed: {list(ALLOWED_INTENTS)}")
        
    # 2. Select Columns existence
    if op.select_columns:
        for col in op.select_columns:
            if col not in df_cols:
                errors.append(f"Column '{col}' requested in selection does not exist. Available: {', '.join(df_cols)}")
                
    # 3. Filters Validation
    if op.filters:
        for idx, f in enumerate(op.filters):
            col = f.column
            if col not in df_cols:
                errors.append(f"Filter condition #{idx+1} references non-existent column '{col}'. Available: {', '.join(df_cols)}")
                continue
                
            if f.operator not in ALLOWED_OPERATORS:
                errors.append(f"Filter condition #{idx+1} on '{col}' uses unsupported operator '{f.operator}'.")
                
            # Value compatibility check
            col_series = df[col]
            val = f.value
            is_numeric_col = pd.api.types.is_numeric_dtype(col_series) and not "bool" in str(col_series.dtype)
            
            if is_numeric_col and f.operator not in ["isnull", "notnull"]:
                if val is not None:
                    # Check if val can be converted to float
                    try:
                        float(str(val))
                    except ValueError:
                        errors.append(f"Value '{val}' in filter condition #{idx+1} is incompatible with numeric column '{col}'.")
                        
    # 4. Sort Columns existence
    if op.sort:
        for idx, s in enumerate(op.sort):
            col = s.column
            if col not in df_cols:
                errors.append(f"Sort condition #{idx+1} references non-existent column '{col}'.")
                
    # 5. Group By Columns existence
    if op.group_by:
        for col in op.group_by:
            if col not in df_cols:
                errors.append(f"Group-by column '{col}' does not exist in dataset.")
                
    # 6. Aggregations Validation
    if op.aggregations:
        for idx, agg in enumerate(op.aggregations):
            col = agg.column
            if col != "*" and col not in df_cols:
                errors.append(f"Aggregation #{idx+1} references non-existent column '{col}'.")
            if agg.func not in ALLOWED_AGGS:
                errors.append(f"Aggregation #{idx+1} uses unsupported function '{agg.func}'. Supported: {list(ALLOWED_AGGS)}")
                
    # 7. Transformations Validation
    if op.transformations:
        for idx, trans in enumerate(op.transformations):
            col = trans.column
            if col not in df_cols:
                errors.append(f"Transformation #{idx+1} references non-existent column '{col}'.")
                continue
            if trans.operation not in ALLOWED_TRANSFORMATIONS:
                errors.append(f"Transformation #{idx+1} uses unsupported operation '{trans.operation}'.")
                
            if trans.operation == "math":
                # Ensure we specify explicit safe operations, e.g., args must contain operator and operand
                math_op = trans.args.get("operator")
                operand = trans.args.get("operand")
                if math_op not in ["+", "-", "*", "/"]:
                    errors.append(f"Math transformation #{idx+1} uses unsupported math operator '{math_op}'. Supported: +, -, *, /")
                if operand is not None:
                    # Check if operand is a numeric value or another column name
                    if str(operand) not in df_cols:
                        try:
                            float(str(operand))
                        except ValueError:
                            errors.append(f"Math transformation #{idx+1} operand '{operand}' must be a number or existing column name.")
                            
    # 8. Limit Boundaries
    if op.limit is not None:
        if op.limit <= 0:
            errors.append(f"Limit value must be a positive integer, got: {op.limit}")
            
    # 9. Visualization Fields existence
    if op.visualization:
        viz = op.visualization
        if viz.x_axis not in df_cols:
            errors.append(f"Visualization X-axis column '{viz.x_axis}' does not exist in dataset.")
        if viz.y_axis and viz.y_axis not in df_cols:
            errors.append(f"Visualization Y-axis column '{viz.y_axis}' does not exist in dataset.")
        if viz.color and viz.color not in df_cols:
            errors.append(f"Visualization color group column '{viz.color}' does not exist.")
            
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_operation_safety(op: StructuredOperation, df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Legacy wrapper for compatibility with original code signature."""
    res = validate_operation(op, df)
    return res["valid"], res["errors"]
