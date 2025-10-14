import streamlit as st
import pandas as pd

st.set_page_config(page_title="FMCG Gap Explorer", layout="centered")
st.title("FMCG Gap Explorer")
st.caption("Top 3 whitespace opportunities per category — simple and clear.")

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
    st.error("Make sure 'skus_enriched.csv' and 'cell_gap_scores.csv' are in the same folder as app.py.")
    st.stop()

# --------------------------
# Helper: generate plain-English recommendation
# --------------------------
def generate_recommendation(row):
    price = str(row['Price_Tier'])
    claim = str(row['Claims'])

    if "200+" in price:
        return f"Premium opportunity: Higher-end {claim if claim != 'none' else ''} products are missing — chance to target affluent buyers."
    elif "101" in price or "201" in price:
        return f"Mid-range opportunity: Everyday shoppers lack {claim if claim != 'none' else ''} choices — scope to expand mainstream options."
    elif "51" in price or "100" in price:
        return f"Value opportunity: Affordable {claim if claim != 'none' else ''} products are missing — scope to win price-sensitive buyers."
    elif "1–50" in price or "₹1" in price:
        return f"Entry-level opportunity: No ultra-low price {claim if claim != 'none' else ''} products — scope to drive trial and volume."
    else:
        return f"Opportunity: Add more {claim if claim != 'none' else ''} products in this price tier."

# --------------------------
# Main logic
# --------------------------
st.subheader("Choose a category")

categories = sorted(cells["category"].unique())
cols = st.columns(3)  # buttons in a grid

for i, cat in enumerate(categories):
    if cols[i % 3].button(cat):
        st.markdown(f"## Top 3 gaps in {cat}")

        # Pick top 3 rows
        gaps = cells[cells["category"] == cat].head(3)

        if gaps.empty:
            st.info("No major gaps found in this category.")
        else:
            for _, row in gaps.iterrows():
                recommendation = generate_recommendation(row)
                st.write(
                    f"- {row['sub_category']} at {row['Price_Tier']} "
                    f"(claims: {row['Claims']}) → {recommendation}"
                )

        st.markdown("---")
