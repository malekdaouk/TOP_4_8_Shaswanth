import streamlit as st
from pathlib import Path
from main import run_pipeline

st.set_page_config(page_title="Proposal Generator", layout="centered")

st.title("Portfolio Proposal Generator")
st.write("Upload the portfolio spreadsheet to generate the proposal.")

# ---------------------------------
# STATIC SECTOR MAPPING PATH
# ---------------------------------

SECTOR_PATH = Path(__file__).parent / "data_files" / "StocksSectorMOCK.xlsx"

if not SECTOR_PATH.exists():
    st.error(f"Sector mapping file not found at: {SECTOR_PATH}")
    st.stop()

# ---------------------------------
# MASTER FILE UPLOAD
# ---------------------------------

master_file = st.file_uploader(
    "Upload Portfolio Spreadsheet",
    type=["xlsx"]
)

# ---------------------------------
# RUN PIPELINE
# ---------------------------------

if master_file is not None:

    if st.button("Generate Report"):

        with st.spinner("Running analytics and building report..."):

            # Open sector file in binary mode
            with open(SECTOR_PATH, "rb") as f:
                ppt_bytes = run_pipeline(master_file, f)

        st.success("Report Ready")

        st.download_button(
            label="Download Report",
            data=ppt_bytes,
            file_name="Proposal_Report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )