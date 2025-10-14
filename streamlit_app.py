import streamlit as st
import pandas as pd

st.set_page_config(page_title="FMCG Gap Explorer", layout="centered")
st.title("FMCG Gap Explorer")
st.caption("See 3 different gaps per category — enriched with claims from SKUs.")

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
# Merge claims from SKUs into cells
# --------------------------
if "Claims" in skus.columns:
    cells = cells.merge(
        skus[["category", "sub_category", "Claims"]],
        on=["category", "sub_category"],
        how="left",
        suffixes=("", "_sku")
    )
    # Prefer SKU claims if available
    cells["Claims"] = cells["Claims_sku"].combine_first(cells.get("Claims"))
    if "Claims_sku" in cells.columns:
        cells.drop(columns=["Claims_sku"], inplace=True)

# --------------------------
# Helper: pick 3 rows preferring real claims
# --------------------------
def pick_top3_with_claims(df, category):
    subset = df[df["category"] == category].copy()

    # Prefer rows where Claims is not "none" or NaN
    claimed = subset[subset["Claims"].notna() & (subset["Claims"].str.lower() != "none")]
    if len(claimed) >= 3:
        return claimed.head(3)
    else:
        filler = subset[subset["Claims"].isna() | (subset["Claims"].str.lower() == "none")]
        return pd.concat([claimed, filler]).drop_duplicates(subset=["sub_category"]).head(3)

# --------------------------
# Main logic
# --------------------------
st.subheader("Choose a category")

categories = sorted(cells["category"].unique())
cols = st.columns(3)  # buttons in a grid

for i, cat in enumerate(categories):
    if cols[i % 3].button(cat):
        st.markdown(f"## Gaps in {cat}")

        gaps = pick_top3_with_claims(cells, cat)

        if gaps.empty:
            st.info("No major gaps found in this category.")
        else:
            for _, row in gaps.iterrows():
                st.write(
                    f"- {row['sub_category']} at {row['Price_Tier']} (claims: {row['Claims']})"
                )

        st.markdown("---")
