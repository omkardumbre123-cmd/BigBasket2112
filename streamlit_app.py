import streamlit as st
import pandas as pd

st.set_page_config(page_title="FMCG Gap Explorer", layout="centered")
st.title("FMCG Gap Explorer")
st.caption("See 3 different gaps per category — simple and clear.")

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
# Helper: pick 3 rows (no claims needed)
# --------------------------
def pick_top3(df, category):
    subset = df[df["category"] == category].copy()
    # Ensure unique sub-categories
    subset = subset.drop_duplicates(subset=["sub_category"])
    return subset.head(3)

# --------------------------
# Main logic
# --------------------------
st.subheader("Choose a category")

categories = sorted(cells["category"].unique())
cols = st.columns(3)  # buttons in a grid

for i, cat in enumerate(categories):
    if cols[i % 3].button(cat):
        st.markdown(f"## Gaps in {cat}")

        gaps = pick_top3(cells, cat)

        if gaps.empty:
            st.info("No major gaps found in this category.")
        else:
            for _, row in gaps.iterrows():
                st.write(
                    f"- {row['sub_category']} at {row['Price_Tier']}"
                )

        st.markdown("---")
