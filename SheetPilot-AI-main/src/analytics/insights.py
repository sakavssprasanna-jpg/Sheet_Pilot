import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

def generate_data_insights(df: pd.DataFrame, before_df: Optional[pd.DataFrame] = None) -> List[str]:
    """
    Generate deterministic, rule-based text insights from a Pandas DataFrame.
    
    Args:
        df: The current/result DataFrame to analyze.
        before_df: Optional DataFrame representing the state before the operation.
        
    Returns:
        A list of string insights describing mathematical facts of the dataset.
    """
    insights = []
    
    if df is None or df.empty:
        return ["The result dataset is empty."]
        
    num_rows = len(df)
    num_cols = len(df.columns)
    
    # 1. Row reduction insight
    if before_df is not None:
        before_rows = len(before_df)
        if before_rows != num_rows:
            pct_change = ((before_rows - num_rows) / before_rows) * 100
            insights.append(
                f"Row Reduction: Dataset size reduced from {before_rows:,} rows to {num_rows:,} rows (reduced by {pct_change:.1f}%)."
            )
            
    # 2. Missing value concentrations
    total_cells = num_rows * num_cols
    missing_cells = df.isnull().sum().sum()
    if missing_cells > 0:
        missing_pct = (missing_cells / total_cells) * 100
        insights.append(
            f"Data Quality: There are {missing_cells:,} missing values in the result ({missing_pct:.1f}% of all cells)."
        )
    else:
        insights.append("Data Quality: The result dataset is 100% complete with zero missing values.")
        
    # Categorize columns
    numeric_cols = []
    categorical_cols = []
    
    for col in df.columns:
        col_str = str(col)
        # Skip potential identifier columns for averages/sums
        is_id = any(x in col_str.lower() for x in ["id", "index", "key"])
        if pd.api.types.is_numeric_dtype(df[col]):
            if not is_id:
                numeric_cols.append(col)
        else:
            categorical_cols.append(col)
            
    # 3. Numeric metrics insights
    for col in numeric_cols[:3]: # Limit to top 3 numeric columns to prevent clutter
        series = df[col].dropna()
        if series.empty:
            continue
            
        col_min = series.min()
        col_max = series.max()
        col_mean = series.mean()
        col_sum = series.sum()
        
        # Friendly formatting helper
        def fmt(val):
            # Check if looks like large numbers
            if abs(val) >= 1_000_000:
                return f"{val/1_000_000:.2f}M"
            elif abs(val) >= 1_000:
                return f"{val:,.2f}"
            elif isinstance(val, (int, np.integer)):
                return f"{val}"
            else:
                return f"{val:.2f}"
                
        # Currency context check
        is_currency = any(x in str(col).lower() for x in ["revenue", "salary", "price", "cost", "amount", "budget"])
        prefix = "₹" if is_currency else ""
        
        insights.append(
            f"Numeric Stats: For '{col}', the total sum is {prefix}{fmt(col_sum)}, average is {prefix}{fmt(col_mean)}, "
            f"ranging from {prefix}{fmt(col_min)} to {prefix}{fmt(col_max)}."
        )
        
    # 4. Categorical insights
    for col in categorical_cols[:2]: # Limit to top 2 categorical columns
        series = df[col].dropna()
        if series.empty:
            continue
            
        value_counts = series.value_counts()
        if value_counts.empty:
            continue
            
        top_cat = value_counts.index[0]
        top_count = value_counts.iloc[0]
        top_pct = (top_count / num_rows) * 100
        
        insights.append(
            f"Categorical Concentration: The most frequent category in '{col}' is '{top_cat}' with {top_count:,} occurrences "
            f"({top_pct:.1f}% of rows)."
        )
        
        if len(value_counts) > 1:
            least_cat = value_counts.index[-1]
            least_count = value_counts.iloc[-1]
            insights.append(
                f"Categorical Concentration: The least frequent category in '{col}' is '{least_cat}' with {least_count:,} occurrences."
            )
            
    return insights
