import pandas as pd
import os
import csv
from typing import Tuple, Optional, Any

def check_duplicate_headers(file_obj: Any, ext: str) -> Optional[str]:
    """Detect duplicate column headers before pandas renames them."""
    try:
        if ext == ".csv":
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
                header_line = file_obj.readline()
                file_obj.seek(0)
                header_str = header_line.decode('utf-8', errors='ignore')
            else:
                with open(file_obj, 'r', encoding='utf-8', errors='ignore') as f:
                    header_str = f.readline()
            
            reader = csv.reader([header_str])
            cols = next(reader)
            cols = [c.strip() for c in cols if c.strip()]
            if len(cols) != len(set(cols)):
                dups = set([x for x in cols if cols.count(x) > 1])
                return f"Duplicate column names detected: {', '.join(dups)}. All column headers must be unique."
                
        elif ext == ".xlsx":
            import openpyxl
            # openpyxl needs a seekable stream or path
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            wb = openpyxl.load_workbook(file_obj, read_only=True)
            sheet = wb.active
            first_row = next(sheet.iter_rows(max_row=1, values_only=True))
            cols = [str(c).strip() for c in first_row if c is not None and str(c).strip()]
            if len(cols) != len(set(cols)):
                dups = set([x for x in cols if cols.count(x) > 1])
                return f"Duplicate column names detected: {', '.join(dups)}. All column headers must be unique."
    except Exception:
        pass
    return None

def load_file(file_obj: Any, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Ingest a spreadsheet file (CSV or Excel) and load it into a pandas DataFrame.
    """
    ext = os.path.splitext(filename.lower())[1]
    
    # 1. Empty file size check
    try:
        if hasattr(file_obj, "seek") and hasattr(file_obj, "tell"):
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(0)
            if size == 0:
                return None, "The uploaded file is empty (0 bytes)."
        elif isinstance(file_obj, str) and os.path.exists(file_obj):
            if os.path.getsize(file_obj) == 0:
                return None, f"The file '{filename}' is empty (0 bytes)."
    except Exception as e:
        return None, f"Failed to verify file size: {str(e)}"

    # 2. Check for duplicates in raw headers
    dup_err = check_duplicate_headers(file_obj, ext)
    if dup_err:
        return None, dup_err

    try:
        if ext == ".csv":
            try:
                df = pd.read_csv(file_obj)
            except UnicodeDecodeError:
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                df = pd.read_csv(file_obj, encoding="latin1")
            except pd.errors.EmptyDataError:
                return None, "The CSV file does not contain any readable columns or data."
            except pd.errors.ParserError as pe:
                return None, f"Malformed CSV structure: {str(pe)}"
                
        elif ext == ".xlsx":
            try:
                df = pd.read_excel(file_obj, engine="openpyxl")
            except Exception as ee:
                return None, f"Invalid Excel file: {str(ee)}"
                
        elif ext == ".xls":
            try:
                import xlrd
            except ImportError:
                return None, "The '.xls' legacy format requires 'xlrd' package which is not installed. Please re-save as '.xlsx' or CSV."
            
            try:
                df = pd.read_excel(file_obj, engine="xlrd")
            except Exception as ee:
                return None, f"Invalid Excel (.xls) file: {str(ee)}"
                
        else:
            return None, f"Unsupported file extension '{ext}'. Please upload a CSV (.csv) or Excel (.xlsx) file."
            
        # Check empty DataFrame load
        if df is None or df.empty:
            return None, "The file was parsed but contains no rows or columns of data."
            
        return df, None
        
    except Exception as e:
        return None, f"Unexpected error reading '{filename}': {str(e)}"
