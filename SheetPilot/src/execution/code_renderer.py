import pandas as pd
from typing import Any
from src.ai.schemas import StructuredOperation

def render_pandas_code(op: StructuredOperation) -> str:
    """
    Renders a validated StructuredOperation into readable Pandas code for review.
    This code is purely for the user's viewing/debugging and is never executed directly.
    """
    if op is None:
        return "# No operation to render."
        
    code_lines = ["# Deterministic pandas operations compiled by SheetPilot AI"]
    code_lines.append("result = df.copy()")
    
    # 1. Transformations
    if op.transformations:
        for trans in op.transformations:
            col = trans.column
            new_col = trans.new_column if trans.new_column else col
            
            if trans.operation == "string_upper":
                code_lines.append(f"result['{new_col}'] = result['{col}'].astype(str).str.upper()")
            elif trans.operation == "string_lower":
                code_lines.append(f"result['{new_col}'] = result['{col}'].astype(str).str.lower()")
            elif trans.operation == "fill_na":
                fill_val = trans.args.get("value", "")
                val_repr = f"'{fill_val}'" if isinstance(fill_val, str) else str(fill_val)
                code_lines.append(f"result['{new_col}'] = result['{col}'].fillna({val_repr})")
            elif trans.operation == "drop_na":
                code_lines.append(f"result = result.dropna(subset=['{col}'])")
            elif trans.operation == "math":
                math_op = trans.args.get("operator")
                operand = trans.args.get("operand")
                
                try:
                    float(str(operand))
                    code_lines.append(f"result['{new_col}'] = pd.to_numeric(result['{col}'], errors='coerce') {math_op} {operand}")
                except ValueError:
                    code_lines.append(f"result['{new_col}'] = pd.to_numeric(result['{col}'], errors='coerce') {math_op} pd.to_numeric(result['{operand}'], errors='coerce')")
                    
    # 2. Filters
    if op.filters:
        for f in op.filters:
            col = f.column
            op_type = f.operator
            val = f.value
            
            val_repr = f"'{val}'" if isinstance(val, str) else str(val)
                
            if op_type == "==":
                code_lines.append(f"result = result[result['{col}'] == {val_repr}]")
            elif op_type == "!=":
                code_lines.append(f"result = result[result['{col}'] != {val_repr}]")
            elif op_type == ">":
                code_lines.append(f"result = result[result['{col}'] > {val_repr}]")
            elif op_type == "<":
                code_lines.append(f"result = result[result['{col}'] < {val_repr}]")
            elif op_type == ">=":
                code_lines.append(f"result = result[result['{col}'] >= {val_repr}]")
            elif op_type == "<=":
                code_lines.append(f"result = result[result['{col}'] <= {val_repr}]")
            elif op_type == "contains":
                code_lines.append(f"result = result[result['{col}'].astype(str).str.contains({val_repr}, case=False, na=False)]")
            elif op_type == "startswith":
                code_lines.append(f"result = result[result['{col}'].astype(str).str.startswith({val_repr}, na=False)]")
            elif op_type == "endswith":
                code_lines.append(f"result = result[result['{col}'].astype(str).str.endswith({val_repr}, na=False)]")
            elif op_type == "isnull":
                code_lines.append(f"result = result[result['{col}'].isnull()]")
            elif op_type == "notnull":
                code_lines.append(f"result = result[result['{col}'].notnull()]")

    # 3. Group By & Aggregation
    if op.aggregations:
        if op.group_by:
            agg_items = []
            for agg in op.aggregations:
                col_name = op.group_by[0] if agg.column == "*" else agg.column
                func_name = "count" if agg.column == "*" else agg.func
                agg_items.append(f"{agg.alias}=pd.NamedAgg(column='{col_name}', aggfunc='{func_name}')")
            agg_str = ", ".join(agg_items)
            code_lines.append(f"result = result.groupby({op.group_by}).agg({agg_str}).reset_index()")
        else:
            flat_agg_items = []
            for agg in op.aggregations:
                col = agg.column
                func = agg.func
                alias = agg.alias
                if col == "*":
                    flat_agg_items.append(f"'{alias}': [len(result)]")
                else:
                    flat_agg_items.append(f"'{alias}': [result['{col}'].{func}()]")
            flat_agg_str = ", ".join(flat_agg_items)
            code_lines.append(f"result = pd.DataFrame({{{flat_agg_str}}})")

    # 4. Sorting
    if op.sort:
        cols = [s.column for s in op.sort]
        ascs = [s.ascending for s in op.sort]
        code_lines.append(f"result = result.sort_values(by={cols}, ascending={ascs})")
        
    # 5. Column Selection
    if op.select_columns:
        code_lines.append(f"result = result[{op.select_columns}]")
        
    # 6. Drop Duplicates
    if op.intent == "duplicate_check":
        code_lines.append("result = result.drop_duplicates()")
        
    # 7. Limit
    if op.limit is not None:
        code_lines.append(f"result = result.head({op.limit})")
        
    return "\n".join(code_lines)
