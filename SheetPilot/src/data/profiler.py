import pandas as pd
import numpy as np
import re
from typing import Dict, Any, List

def infer_semantic_type(col_name: str, series: pd.Series, unique_count: int, uniqueness_ratio: float) -> str:
    """
    Safely infer the semantic type of a Pandas Series based on column name and values.
    Possible outputs: 'numeric', 'categorical', 'date', 'datetime', 'boolean', 'text', 'identifier', 'currency-like', 'percentage-like'
    """
    name_lower = str(col_name).lower()
    non_nulls = series.dropna()
    
    if len(non_nulls) == 0:
        return "text"
        
    dtype_str = str(series.dtype)
    
    # 1. Check Boolean
    if "bool" in dtype_str:
        return "boolean"
    if unique_count <= 2:
        vals = set(non_nulls.astype(str).str.lower().unique())
        if vals.issubset({"true", "false", "t", "f", "1", "0", "yes", "no", "y", "n"}):
            return "boolean"
            
    # 2. Check Identifier
    if unique_count == len(series) and (("id" in name_lower) or ("code" in name_lower) or ("key" in name_lower) or ("num" in name_lower) or "index" in name_lower):
        return "identifier"
    if name_lower in ["id", "key", "pk", "uuid", "guid"]:
        return "identifier"

    # 3. Check Date/Datetime
    if "datetime" in dtype_str or "timestamp" in dtype_str:
        return "datetime"
    if "date" in name_lower or "time" in name_lower or "created" in name_lower or "updated" in name_lower:
        try:
            samples = non_nulls.head(3).astype(str)
            pd.to_datetime(samples, errors="raise")
            return "date" if "time" not in name_lower else "datetime"
        except Exception:
            pass

    # 4. Check Percentage-like
    pct_keywords = ["rate", "pct", "percent", "percentage", "ratio"]
    if any(k in name_lower for k in pct_keywords):
        return "percentage-like"
    sample_str = str(non_nulls.iloc[0]).strip()
    if sample_str and sample_str.endswith("%"):
        return "percentage-like"

    # 5. Check Currency-like
    currency_keywords = ["price", "salary", "revenue", "cost", "amount", "money", "wage", "budget", "sales", "spend"]
    if any(k in name_lower for k in currency_keywords):
        return "currency-like"
    if sample_str and (sample_str[0] in ["$", "€", "£", "₹"] or re.match(r'^[A-Z]{3}\s?\d', sample_str)):
        return "currency-like"

    # 6. Numeric check
    if pd.api.types.is_numeric_dtype(series):
        if unique_count <= 10 and pd.api.types.is_integer_dtype(series):
            return "categorical"
        return "numeric"

    # 7. Categorical vs Text
    if unique_count <= 20 or uniqueness_ratio < 0.15:
        return "categorical"
        
    return "text"

def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Profile a Pandas DataFrame to extract dimensions, column schema, missing values, 
    statistics, semantic types, and sample data.
    """
    if df is None or df.empty:
        return {
            "shape": {"rows": 0, "cols": 0},
            "columns": [],
            "numeric_columns": [],
            "categorical_columns": [],
            "stats": {},
            "sample": [],
            "memory_usage_bytes": 0,
            "duplicate_rows": 0,
            "total_missing_cells": 0,
            "data_quality_score": 100.0
        }
        
    total_rows, total_cols = df.shape
    total_cells = total_rows * total_cols
    
    # Calculate dataset level stats
    memory_usage = int(df.memory_usage(deep=True).sum())
    duplicate_rows = int(df.duplicated().sum())
    total_missing = int(df.isnull().sum().sum())
    
    if total_cells > 0:
        missing_factor = (total_cells - total_missing) / total_cells
        missing_pct = (total_missing / total_cells) * 100
    else:
        missing_factor = 1.0
        missing_pct = 0.0

    duplicate_factor = (total_rows - duplicate_rows) / total_rows if total_rows > 0 else 1.0
    
    empty_cols_count = sum(1 for col in df.columns if df[col].isnull().all())
    completeness_factor = (total_cols - empty_cols_count) / total_cols if total_cols > 0 else 1.0
    
    mixed_cols_count = 0
    for col in df.columns:
        inf_type = pd.api.types.infer_dtype(df[col].dropna())
        if "mixed" in inf_type:
            mixed_cols_count += 1
    consistency_factor = (total_cols - mixed_cols_count) / total_cols if total_cols > 0 else 1.0
    
    quality_score = (
        (missing_factor * 0.40) + 
        (duplicate_factor * 0.30) + 
        (completeness_factor * 0.15) + 
        (consistency_factor * 0.15)
    ) * 100.0


    columns_info = []
    numeric_cols = []
    categorical_cols = []
    
    stats = {}
    
    for col in df.columns:
        col_str = str(col)
        series = df[col]
        dtype = str(series.dtype)
        null_count = int(series.isnull().sum())
        null_pct = float((null_count / total_rows) * 100) if total_rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))
        uniqueness_ratio = float(unique_count / total_rows) if total_rows > 0 else 0.0
        
        # Infer semantic type
        semantic_type = infer_semantic_type(col_str, series, unique_count, uniqueness_ratio)
        
        # Sample values representation (up to 5 unique non-null samples)
        unique_samples = series.dropna().unique()[:5]
        samples_list = [str(x) for x in unique_samples]
        
        col_meta = {
            "name": col_str,
            "dtype": dtype,
            "null_count": null_count,
            "null_pct": round(null_pct, 2),
            "unique_count": unique_count,
            "uniqueness_ratio": round(uniqueness_ratio, 4),
            "semantic_type": semantic_type,
            "samples": samples_list
        }
        
        # Calculate stats based on inferred semantic / pandas dtype
        is_num = pd.api.types.is_numeric_dtype(series) and not "bool" in dtype
        if is_num:
            numeric_cols.append(col_str)
            col_stats = {
                "count": int(series.count()),
                "mean": float(series.mean()) if series.count() > 0 else None,
                "std": float(series.std()) if series.count() > 1 else None,
                "min": float(series.min()) if series.count() > 0 else None,
                "max": float(series.max()) if series.count() > 0 else None,
                "median": float(series.median()) if series.count() > 0 else None,
            }
            # Round clean values
            for k, v in col_stats.items():
                if v is not None:
                    col_stats[k] = round(v, 4)
            stats[col_str] = col_stats
        else:
            categorical_cols.append(col_str)
            val_counts = series.value_counts(dropna=True)
            if not val_counts.empty:
                top_val = val_counts.index[0]
                top_freq = val_counts.iloc[0]
                stats[col_str] = {
                    "count": int(series.count()),
                    "unique_count": unique_count,
                    "top": str(top_val),
                    "freq": int(top_freq),
                    "freq_pct": round(float((top_freq / total_rows) * 100), 2) if total_rows > 0 else 0.0
                }
            else:
                stats[col_str] = {
                    "count": 0,
                    "unique_count": 0,
                    "top": None,
                    "freq": 0,
                    "freq_pct": 0.0
                }
                
        columns_info.append(col_meta)
        
    # Sample rows representation for rendering
    sample_df = df.head(5).copy()
    for col in sample_df.columns:
        if sample_df[col].dtype == object or isinstance(sample_df[col].dtype, pd.CategoricalDtype):
            sample_df[col] = sample_df[col].fillna("")
        else:
            sample_df[col] = sample_df[col].where(pd.notnull(sample_df[col]), None)
            
    sample_df.columns = sample_df.columns.map(str)
    sample_rows = sample_df.to_dict(orient="records")
    
    profile = {
        "shape": {
            "rows": total_rows,
            "cols": total_cols
        },
        "columns": columns_info,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "stats": stats,
        "sample": sample_rows,
        "memory_usage_bytes": memory_usage,
        "duplicate_rows": duplicate_rows,
        "total_missing_cells": total_missing,
        "missing_pct": round(missing_pct, 2),
        "data_quality_score": round(quality_score, 2),
        "data_quality_breakdown": {
            "missing_factor": round(missing_factor * 100, 2),
            "duplicate_factor": round(duplicate_factor * 100, 2),
            "completeness_factor": round(completeness_factor * 100, 2),
            "consistency_factor": round(consistency_factor * 100, 2),
            "empty_cols": empty_cols_count,
            "mixed_cols": mixed_cols_count
        }
    }
    
    return profile
