import streamlit as st
import pandas as pd

st.set_page_config(page_title="FMCG Gap Finder", layout="wide")

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
except Exception as e:
    st.error("Make sure 'skus_enriched.csv' and 'cell_gap_scores.csv' are in the same folder as app.py.")
    st.stop()

# --------------------------
# Main
# --------------------------
st.title("FMCG Portfolio Gap Finder")

# Threshold for what counts as a 'gap'
gap_threshold = st.sidebar.slider("Gap Score threshold", 0.5, 0.95, 0.7, 0.05)

# Filter cells above threshold
gaps = cells[cells["Gap_Score"] >= gap_threshold].copy()
gaps = gaps.sort_values("Gap_Score", ascending=False)

st.subheader("Identified Gaps")
if gaps.empty:
    st.info("No gaps found above the selected threshold.")
else:
    st.dataframe(
        gaps[["category", "sub_category", "Price_Tier", "Claims", "Gap_Score"]],
        use_container_width=True
    )

    # Simple descriptive recommendations
    st.subheader("What can be done")
    for _, row in gaps.iterrows():
        st.write(
            f"- In **{row['category']} / {row['sub_category']}**, "
            f"the **{row['Price_Tier']}** tier with claim **{row['Claims']}** "
            f"shows a gap (score {row['Gap_Score']:.2f}). "
            f"👉 Consider launching or repositioning SKUs here to capture unmet demand."
        )
