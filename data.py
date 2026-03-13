import pandas as pd
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# -----------------------------------------------------
# CACHE DATABASE FILES
# -----------------------------------------------------

@st.cache_data
def load_symbol_database():

    path = BASE_DIR / "data_files" / "SymbolInfo313UpdateWeekly.xlsx"

    df = pd.read_excel(path)

    df.columns = df.columns.str.strip()

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


@st.cache_data
def load_benchmarks():

    path = BASE_DIR / "data_files" / "Benchmarks.xlsx"

    df = pd.read_excel(path)

    df.columns = df.columns.str.strip()

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


@st.cache_data
def load_sector_database():

    path = BASE_DIR / "data_files" / "StocksSectorMOCK.xlsx"

    df = pd.read_excel(path)

    df.columns = df.columns.str.strip()

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


# -----------------------------------------------------
# BUILD MASTER DATAFRAME
# -----------------------------------------------------

def build_master_dataframe(holdings_file):

    holdings = pd.read_excel(holdings_file)

    holdings.columns = holdings.columns.str.strip()

    holdings["Symbol"] = (
        holdings["Symbol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    db = load_symbol_database()
    benchmarks = load_benchmarks()
    sectors = load_sector_database()

    # ---------------------------------
    # MERGE HOLDINGS + SYMBOL DATABASE
    # ---------------------------------

    merged = holdings.merge(db, on="Symbol", how="left")

    missing = merged[merged["Name"].isna()]["Symbol"].unique()

    if len(missing) > 0:

        print("\nSkipping symbols not found in SymbolInfo313UpdateWeekly:")

        for s in sorted(missing):
            print(s)

        merged = merged[~merged["Symbol"].isin(missing)]

    # ---------------------------------
    # APPEND BENCHMARKS
    # ---------------------------------

    benchmarks["Market Value"] = 0
    benchmarks["Unrealized"] = 0
    benchmarks["Q/NQ"] = "Index"
    benchmarks["Account"] = "Benchmark"

    merged = pd.concat([merged, benchmarks], ignore_index=True)

    # ---------------------------------
    # ADD REQUIRED SP500 ROW
    # ---------------------------------

    if "SP500" not in merged["Q/NQ"].values:

        sp500_row = {col: 0 for col in merged.columns}

        sp500_row["Q/NQ"] = "SP500"
        sp500_row["Account"] = "Benchmark"
        sp500_row["Symbol"] = "SP500"
        sp500_row["Market Value"] = 0

        merged = pd.concat(
            [merged, pd.DataFrame([sp500_row])],
            ignore_index=True
        )

    # ---------------------------------
    # MERGE SECTOR DATA
    # ---------------------------------

    merged = merged.merge(
        sectors[["Symbol", "Sector"]],
        on="Symbol",
        how="left"
    )

    missing_sector = merged[merged["Sector"].isna()]["Symbol"].unique()

    if len(missing_sector) > 0:

        print("\nSymbols missing sector mapping:")

        for s in sorted(missing_sector):
            print(s)

    merged["Sector"] = merged["Sector"].fillna("UNKNOWN")

    return merged


# -----------------------------------------------------
# PREPARE DATA FOR MATH ENGINE
# -----------------------------------------------------

def prepare_data(master_file):

    df = pd.read_excel(master_file)

    df.columns = df.columns.str.strip()

    df["Market Value"] = pd.to_numeric(
        df["Market Value"],
        errors="coerce"
    ).fillna(0)

    if "Sector" not in df.columns:
        df["Sector"] = "UNKNOWN"

    # -------------------------------
    # FORCE TEXT COLUMNS
    # -------------------------------

    text_cols = [
        "Q/NQ",
        "Account",
        "Symbol",
        "Sector",
        "equity_style",
        "fixed_income_style",
        "broad_asset_class",
        "category_name",
        "index_fund",
        "Name",
        "fund_family",
        "share_class",
        "hq_country",
        "detailed_security_type"
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)

    style_rows_with_ERR = df.copy()

    # -------------------------------
    # FORCE NUMERIC COLUMNS
    # -------------------------------

    exclude_cols = text_cols

    numeric_cols = [
        c for c in df.columns
        if c not in exclude_cols
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df, style_rows_with_ERR