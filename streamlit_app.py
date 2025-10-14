import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import random

st.set_page_config(page_title="FMCG Gap Explorer", layout="wide")
st.title("FMCG Gap Explorer")
st.caption("Top 3 whitespace opportunities per category, with visuals for context.")

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
# Helper: generate placeholder image
# --------------------------
def create_placeholder(category: str):
    # Random pastel background
    colors = [(200, 230, 255), (220, 255, 200), (255, 230, 200), (240, 220, 255)]
    bg_color = random.choice(colors)

    img = Image.new("RGB", (300, 200), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load a default font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Center text
    text = category
    w, h = draw.textsize(text, font=font)
    draw.text(((300 - w) / 2, (200 - h) / 2), text, fill="black", font=font)

    return img

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
            st.subheader("Opportunities")
            for _, row in gaps.iterrows():
                recommendation = generate_recommendation(row)
                st.write(
                    f"- {row['sub_category']} at {row['Price_Tier']} "
                    f"(claims: {row['Claims']}) → {recommendation}"
                )

            # --------------------------
            # Show SKU images if available, else generate placeholders
            # --------------------------
            st.subheader("Product Examples")

            if "p_url" in skus.columns:
                sample_skus = skus[(skus["category"] == cat)].head(3)
                if not sample_skus.empty and "http" in str(sample_skus.iloc[0].get("p_url", "")):
                    img_cols = st.columns(len(sample_skus))
                    for j, (_, sku) in enumerate(sample_skus.iterrows()):
                        with img_cols[j]:
                            st.image(sku["p_url"], caption=sku.get("product", "SKU"), use_container_width=True)
                else:
                    # Generate placeholders
                    img_cols = st.columns(3)
                    for j in range(3):
                        with img_cols[j]:
                            st.image(create_placeholder(cat), caption=f"{cat} Example", use_container_width=True)
            else:
                img_cols = st.columns(3)
                for j in range(3):
                    with img_cols[j]:
                        st.image(create_placeholder(cat), caption=f"{cat} Example", use_container_width=True)

        st.markdown("---")
