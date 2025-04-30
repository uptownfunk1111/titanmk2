import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="TITAN Tipping Dashboard", layout="wide")

st.title("🏉 TITAN 2.5 — NRL Tipping AI Dashboard")
st.markdown("Built by Sam Langston | Tactical Intelligence Tipping for NRL")

# Load data
TIPS_FILE = "outputs/titan_tips.xlsx"

if not os.path.exists(TIPS_FILE):
    st.error("❌ Tip file not found. Please run `titan_main.py` first.")
    st.stop()

df = pd.read_excel(TIPS_FILE)

# 🔍 Debug: show actual column names
st.write("🔍 Columns in your Excel file:", df.columns.tolist())

# Show first few rows
st.markdown("### Sample Data:")
st.dataframe(df.head(), use_container_width=True)

st.sidebar.info("⚙️ Filters will activate once column names are confirmed.")

st.caption("Version 2.5 | Streamlit-powered dashboard | © 2025 Sam Langston")
