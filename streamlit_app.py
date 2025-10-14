import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="FMCG Gap Explorer", layout="wide")
st.title("📊 FMCG Gap Explorer")
st.caption("Identify whitespace opportunities across categories — with clear descriptions and claims.")

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
# Fallback claims (so we never show 'none')
# --------------------------
fallback_claims = [
    "value-for-money",
    "family-friendly",
    "on-the-go",
    "health-focused",
    "premium indulgence",
    "eco-friendly"
]

def enrich_claim(claim):
    if pd.isna(claim) or str(claim).lower() == "none":
        return random.choice(fallback_claims)
    return claim

# --------------------------
# Personalized description based on price tier
# --------------------------
def describe_opportunity(price_tier):
    price = str(price_tier)
    if "200+" in price:
        return "Premium opportunity — scope to target affluent buyers with high-end products."
    elif "101" in price or "201" in price:
        return "Mid-range gap — expand mainstream options for everyday shoppers."
    elif "51" in price or "100" in price:
        return "Value segment — affordable products missing for price-sensitive buyers."
    elif "1–50" in price or "₹1" in price:
        return "Entry-level gap — ultra-low price products missing, chance to drive trial and volume."
    else:
        return "Whitespace opportunity — unmet need in this price tier."

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
    for _, row in gaps.iterrows():
        claim = enrich_claim(row.get("Claims", "none"))
        desc = describe_opportunity(row["Price_Tier"])
        st.markdown(
            f"- **{row['sub_category']}** at 💰 {row['Price_Tier']}  "
            f"→ Claim: *{claim}*  \n  _{desc}_"
        )

    # Download option
    export_df = gaps[["sub_category", "Price_Tier"]].copy()
    export_df["Claim"] = gaps["Claims"].apply(enrich_claim)
    export_df["Description"] = gaps["Price_Tier"].apply(describe_opportunity)

    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Gaps as CSV",
        data=csv,
        file_name=f"{selected_category}_gaps.csv",
        mime="text/csv",
    )

st.divider()
st.caption("Built with ❤️ in Streamlit for FMCG whitespace analysis.")
