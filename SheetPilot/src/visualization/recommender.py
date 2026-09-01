import pandas as pd
import numpy as np
from typing import Optional
from src.ai.schemas import VisualizationConfig

def recommend_chart(df: pd.DataFrame, last_op_intent: Optional[str] = None) -> Optional[VisualizationConfig]:
    """
    Automatically recommends a visualization config based on the data shape and types.
    
    Args:
        df: The pandas DataFrame to analyze.
        last_op_intent: Optional string indicating the last operation's intent.
        
    Returns:
        A VisualizationConfig if a visualization is recommended, or None if table view is best.
    """
    if df is None or df.empty:
        return None
        
    cols = list(df.columns)
    num_rows = len(df)
    
    # Identify column types
    numeric_cols = []
    categorical_cols = []
    datetime_cols = []
    
    for col in cols:
        col_str = str(col)
        # Skip ID columns for numeric calculations if other numeric columns exist
        is_id = any(x in col_str.lower() for x in ["id", "index", "key"])
        
        # Check datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        elif any(x in col_str.lower() for x in ["date", "year", "month", "timestamp"]):
            # Try converting to datetime to verify
            try:
                pd.to_datetime(df[col].head(5), errors='raise')
                datetime_cols.append(col)
            except Exception:
                categorical_cols.append(col)
        # Check numeric
        elif pd.api.types.is_numeric_dtype(df[col]):
            if is_id:
                # Keep ID columns as fallback categorical or low priority numeric
                categorical_cols.append(col)
            else:
                numeric_cols.append(col)
        # Otherwise treat as categorical
        else:
            categorical_cols.append(col)
            
    # If no non-ID numeric columns, check if any ID/numeric columns exist
    if not numeric_cols:
        all_numeric = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
        if all_numeric:
            numeric_cols = [all_numeric[0]]

    # Case 1: Time series trend (Date + Numeric)
    if datetime_cols and numeric_cols:
        return VisualizationConfig(
            chart_type="line",
            x_axis=datetime_cols[0],
            y_axis=numeric_cols[0],
            title=f"{numeric_cols[0]} Trend Over Time"
        )
        
    # Case 2: Categorical + Numeric (e.g. aggregates, categories)
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        unique_cats = df[cat_col].nunique()
        
        # Extremely small distribution -> Pie Chart
        if 2 <= unique_cats <= 5:
            return VisualizationConfig(
                chart_type="pie",
                x_axis=cat_col,
                y_axis=num_col,
                title=f"Distribution of {num_col} by {cat_col}"
            )
        # Standard size category list -> Bar Chart
        elif 2 <= unique_cats <= 30:
            return VisualizationConfig(
                chart_type="bar",
                x_axis=cat_col,
                y_axis=num_col,
                title=f"{num_col} by {cat_col}"
            )
            
    # Case 3: Correlation (Numeric vs Numeric)
    if len(numeric_cols) >= 2:
        return VisualizationConfig(
            chart_type="scatter",
            x_axis=numeric_cols[0],
            y_axis=numeric_cols[1],
            title=f"{numeric_cols[1]} vs {numeric_cols[0]}"
        )
        
    # Case 4: Distribution of a single numeric column
    if len(numeric_cols) == 1 and num_rows > 5:
        return VisualizationConfig(
            chart_type="histogram",
            x_axis=numeric_cols[0],
            title=f"Distribution of {numeric_cols[0]}"
        )
        
    # Default: No clear chart recommendation, use Table view
    return None
