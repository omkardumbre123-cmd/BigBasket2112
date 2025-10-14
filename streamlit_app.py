import streamlit as st
import pandas as pd

st.set_page_config(page_title="FMCG Gap Explorer", layout="centered")
st.title("FMCG Gap Explorer")
st.caption("Identify whitespace opportunities by category and price tier with clear, actionable insights.")

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
# Helper: generate tailored description
# --------------------------
def generate_recommendation(row):
    price = str(row['Price_Tier'])
    claim = str(row['Claims'])

    # Map numeric ranges into tiers
    if "200+" in price or "₹200" in price or "₹300" in price or "₹500" in price:
        return f"Premium gap: Higher-end {claim if claim != 'none' else ''} products are missing — scope to target affluent buyers."
    elif "101" in price or "201" in price:
        return f"Mid-tier gap: Mainstream {claim if claim != 'none' else ''} options are underrepresented — scope to attract everyday shoppers."
    elif "51" in price or "100" in price:
        return f"Value gap: Affordable {claim if claim != 'none' else ''} products are missing — scope to capture price-sensitive buyers."
    elif "1–50" in price or "₹1" in price:
        return f"Entry-level gap: Ultra-low price {claim if claim != 'none' else ''} products are absent — scope to drive trial and volume."
    else:
        return f"Gap in {price} tier with {claim} claims — scope to expand assortment."

# --------------------------
# Main logic
# --------------------------
gap_threshold = 0.7  # backend filter

st.subheader("Choose a category to explore gaps")

categories = sorted(cells["category"].unique())
cols = st.columns(3)  # 3 buttons per row

for i, cat in enumerate(categories):
    if cols[i % 3].button(cat):
        st.markdown(f"### Gaps in {cat}")
        gaps = cells[(cells["category"] == cat) & (cells["Gap_Score"] >= gap_threshold)]
        
        if gaps.empty:
            st.info("No significant gaps found in this category.")
        else:
            for _, row in gaps.iterrows():
                recommendation = generate_recommendation(row)
                st.write(
                    f"- {row['sub_category']} at {row['Price_Tier']} "
                    f"(claims: {row['Claims']}) → {recommendation}"
                )

        st.markdown("---")
