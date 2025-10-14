import streamlit as st
import pandas as pd

st.set_page_config(page_title="FMCG Gap Explorer", layout="wide")
st.title("FMCG Gap Explorer")
st.caption("Top 3 whitespace opportunities per category, with product visuals for context.")

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
# Fallback category images
# --------------------------
category_images = {
    "Bakery, Cakes & Dairy": [
        "https://milkbarstore.com/cdn/shop/products/birthday-cake.jpg",
        "https://store.portosbakery.com/cdn/shop/products/milk-n-berries-cake.jpg"
    ],
    "Beverages": [
        "https://images.unsplash.com/photo-1580910051074-7d4f3f3a7f4f",
        "https://images.unsplash.com/photo-1604908177522-040b8f67e0f7"
    ],
    "Snacks": [
        "https://images.unsplash.com/photo-1606788075761-1f7b6f3c9f3f",
        "https://images.unsplash.com/photo-1589308078055-7a4a1a2e2f3f"
    ],
    "Fruits & Vegetables": [
        "https://images.unsplash.com/photo-1572441710534-680c6f3c9f3f",
        "https://images.unsplash.com/photo-1606788075761-1f7b6f3c9f3f"
    ],
    "Frozen Snacks": [
        "https://www.thekitchn.com/thmb/best-frozen-snacks.jpg",
        "https://www.eater.com/thmb/frozen-snacks.jpg"
    ],
    "Ready to Cook": [
        "https://www.mtrfoods.com/wp-content/uploads/2021/07/ready-to-cook.jpg",
        "https://www.nilons.com/images/ready-to-cook.jpg"
    ],
    "Condiments & Sauces": [
        "https://sporked.com/wp-content/uploads/2022/05/best-condiments.jpg",
        "https://www.seriouseats.com/thmb/hot-sauces.jpg"
    ],
    "Pantry Staples": [
        "https://www.thespruceeats.com/thmb/pantry-staples.jpg",
        "https://www.allrecipes.com/thmb/pantry-essentials.jpg"
    ],
    "Gardening Tools": [
        "https://www.homedepot.com/p/9-Piece-Stainless-Steel-Gardening-Tools.jpg",
        "https://www.amazon.com/Garden-Set-Gardening-Ergonomic/dp/B08JHYMV4W"
    ],
    "Pots & Planters": [
        "https://www.amazon.com/GARDIFE-planters-Indoor-Plants-Flower/dp/B0CGF34GT8",
        "https://www.homedepot.com/p/Algreen-PRODUCTS-20-in-Tall-Crete-Planter.jpg"
    ],
    "Prayer Accessories": [
        "https://www.amazon.com/Tasbih-Turquoise-Misbaha-Islamic-Accessories/dp/B09GYSF299",
        "https://www.dharmashop.com/products/tibetan-prayer-wheel-hand-held-8-symbols"
    ],
    "Spiritual Books": [
        "https://www.oprahdaily.com/entertainment/books/g40575967/spiritual-books/",
        "https://www.amazon.com/Prophet-Spirituality-Classic-Capstone-Classics/dp/0857088556"
    ]
    # You can keep expanding this dictionary for all categories in your dataset
}

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
            # Show SKU images if available, else fallback category images
            # --------------------------
            st.subheader("Product Examples")

            if "p_url" in skus.columns:
                sample_skus = skus[(skus["category"] == cat)].head(3)
                if not sample_skus.empty:
                    img_cols = st.columns(len(sample_skus))
                    for j, (_, sku) in enumerate(sample_skus.iterrows()):
                        with img_cols[j]:
                            st.image(sku["p_url"], caption=sku.get("product", "SKU"), use_container_width=True)
                else:
                    if cat in category_images:
                        st.image(category_images[cat], use_container_width=True)
            else:
                if cat in category_images:
                    st.image(category_images[cat], use_container_width=True)

        st.markdown("---")
