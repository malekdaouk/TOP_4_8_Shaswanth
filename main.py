from data import prepare_data
from math_engine import run_calculations
from ppt import build_master_report


def run_pipeline(master_file, sector_file):

    # STEP 1 — Data
    df, err = prepare_data(master_file, sector_file)
    results = run_calculations(df, err)

    # STEP 2 — Build single master deck
    ppt_bytes = build_master_report(results)

    return ppt_bytes