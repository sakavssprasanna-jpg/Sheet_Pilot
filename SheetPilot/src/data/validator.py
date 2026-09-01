import pandas as pd
from typing import List, Tuple

def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    """
    Validate the structural integrity of the DataFrame.
    
    Args:
        df: The pandas DataFrame to validate.
        
    Returns:
        A tuple of (is_valid, errors, warnings).
        - is_valid: True if no critical errors are found.
        - errors: List of critical errors (e.g. empty dataset, duplicate column names).
        - warnings: List of issues that don't block operation but might cause problems.
    """
    errors = []
    warnings = []
    
    if df is None:
        errors.append("DataFrame is None.")
        return False, errors, warnings
        
    if df.empty:
        errors.append("DataFrame is empty (no rows or columns).")
        return False, errors, warnings
        
    rows, cols = df.shape
    if rows == 0:
        errors.append("Dataset contains 0 rows.")
    if cols == 0:
        errors.append("Dataset contains 0 columns.")
        
    if errors:
        return False, errors, warnings
        
    # Check for unnamed columns (often happens with bad indices or headers)
    unnamed_cols = [str(col) for col in df.columns if str(col).startswith("Unnamed:")]
    if unnamed_cols:
        warnings.append(f"Found {len(unnamed_cols)} unnamed column(s) (e.g. '{unnamed_cols[0]}'). These might be index columns.")
        
    # Check for completely null columns
    all_null_cols = []
    for col in df.columns:
        if df[col].isnull().all():
            all_null_cols.append(str(col))
    if all_null_cols:
        warnings.append(f"The following columns are completely empty: {', '.join(all_null_cols[:5])}")
        
    # Check if duplicate columns exist
    dup_cols = df.columns[df.columns.duplicated()].map(str).tolist()
    if dup_cols:
        errors.append(f"Duplicate column names detected: {', '.join(set(dup_cols))}")
        
    # Warning if the dataset is extremely large (warning about performance)
    if rows > 100000:
        warnings.append(f"Large dataset detected ({rows:,} rows). Complex AI operations might run slowly.")
        
    is_valid = len(errors) == 0
    return is_valid, errors, warnings
