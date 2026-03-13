from io import BytesIO
import streamlit as st
import pandas as pd

from data import build_master_dataframe
from main import run_pipeline

st.set_page_config(page_title="Portfolio Analyzer", layout="centered")

st.title("Portfolio Analyzer")
st.write("Upload a holdings file to generate the portfolio report.")

# -----------------------------------------------------
# Upload Holdings
# -----------------------------------------------------

holdings_file = st.file_uploader(
    "Upload Holdings File",
    type=["xlsx"]
)

# -----------------------------------------------------
# Process
# -----------------------------------------------------

if holdings_file is not None:

    try:

        with st.spinner("Building master dataset..."):

            master_df = build_master_dataframe(holdings_file)

            if master_df.empty:
                st.error("No valid symbols found after merge with MasterTemplate2.")
                st.stop()

        # -----------------------------------------------------
        # Ensure required columns exist
        # -----------------------------------------------------

        master_df.columns = master_df.columns.str.strip()

        column_fix = {
            "MarketValue": "Market Value",
            "Market_Value": "Market Value",
            "Market Value $": "Market Value",
            "Unrealised": "Unrealized"
        }

        master_df = master_df.rename(columns=column_fix)

        required_cols = [
            "Q/NQ",
            "Account",
            "Symbol",
            "Market Value",
            "Unrealized"
        ]

        missing = [c for c in required_cols if c not in master_df.columns]

        if missing:
            st.error(f"Missing required columns: {missing}")
            st.write("Detected columns:")
            st.write(master_df.columns)
            st.stop()

        st.success(f"{len(master_df)} holdings successfully processed.")

        # -----------------------------------------------------
        # Convert dataframe → Excel buffer
        # -----------------------------------------------------

        buffer = BytesIO()
        master_df.to_excel(buffer, index=False)
        buffer.seek(0)

        # -----------------------------------------------------
        # Run analytics pipeline
        # -----------------------------------------------------

        with st.spinner("Running portfolio calculations..."):

            ppt_bytes = run_pipeline(buffer)

        st.success("Portfolio analysis complete.")

        # -----------------------------------------------------
        # Download report
        # -----------------------------------------------------

        st.download_button(
            label="Download Portfolio Report",
            data=ppt_bytes,
            file_name="Portfolio_Report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

        # -----------------------------------------------------
        # Preview master dataset
        # -----------------------------------------------------

        with st.expander("Preview Master Dataset"):
            st.dataframe(master_df, use_container_width=True)

    except Exception as e:

        st.error("An error occurred while processing the file.")
        st.exception(e)