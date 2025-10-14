import streamlit as st
import pandas as pd

st.set_page_config(page_title="FMCG Gap Explorer", layout="wide")
st.title("📊 FMCG Gap Explorer")
st.caption("Identify whitespace opportunities across categories — simple, clear, and professional.")

# --------------------------
# Load data
# --------------------------
@st.cache_data
def load_data():
    skus = pd.read_csv("skus_enriched.csv")
    cells = pd.read_csv("cell_gap_scores.csv")
    return skus, cells

try:
    skus, cells = load_data()
except Exception:
    st.error("⚠️ Make sure 'skus_enriched.csv' and 'cell_gap_scores.csv' are in the same folder as app.py.")
    st.stop()

# --------------------------
# Helper: pick 3 different sub-categories
# --------------------------
def pick_three(df, category):
    subset = df[df["category"] == category].copy()
    subset = subset.drop_duplicates(subset=["sub_category"])
    return subset.head(3)

# --------------------------
# Sidebar filters
# --------------------------
st.sidebar.header("🔎 Filters")
categories = sorted(cells["category"].unique())
selected_category = st.sidebar.selectbox("Choose a category", categories)

# --------------------------
# Main display
# --------------------------
st.subheader(f"Gaps in {selected_category}")

gaps = pick_three(cells, selected_category)

if gaps.empty:
    st.info("No major gaps found in this category.")
else:
    # Show as a clean table
    display_df = gaps[["sub_category", "Price_Tier"]].rename(
        columns={"sub_category": "Sub-Category", "Price_Tier": "Price Tier"}
    )
    st.table(display_df)

    # Download button
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Gaps as CSV",
        data=csv,
        file_name=f"{selected_category}_gaps.csv",
        mime="text/csv",
    )

st.divider()
st.caption("Built with ❤️ in Streamlit for FMCG whitespace analysis.")
