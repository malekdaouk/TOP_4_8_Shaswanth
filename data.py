import pandas as pd
import numpy as np
import copy

def prepare_data(master_file, sector_file):

    # ===== READ FILES (works for Streamlit uploads OR local paths) =====
    df = pd.read_excel(master_file)
    stocks_sectors = pd.read_excel(sector_file)

    # ===== STANDARDIZE COLUMN NAMES =====
    df.columns = df.columns.str.strip()
    stocks_sectors.columns = stocks_sectors.columns.str.strip()

    # ===== MERGE SECTOR MAPPING =====
    if "Symbol" in df.columns and "Symbol" in stocks_sectors.columns:
        df = df.merge(
            stocks_sectors[["Symbol", "Sector"]],
            on="Symbol",
            how="left"
        )

    # ===== SNAPSHOT BEFORE MODIFICATION (for error highlighting later) =====
    style_rows_with_ERR = df.copy()

    # ===== NUMERIC CONVERSION =====
    exclude_cols = [
        "Q/NQ","Account","Symbol","broad_asset_class","detailed_security_type",
        "category_name","index_fund","equity_style","fixed_income_style",
        "Name","fund_family","share_class","hq_country","Sector"
    ]

    numeric_cols = [c for c in df.columns if c not in exclude_cols]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ===== NORMALIZE ALPHA COLUMNS (only if present) =====
    alpha_cols = [
        "alpha_1y_vs_category",
        "alpha_3y_vs_category",
        "alpha_5y_vs_category"
    ]

    for col in alpha_cols:
        if col in df.columns:
            df[col] = df[col] / 100

    return df, style_rows_with_ERR