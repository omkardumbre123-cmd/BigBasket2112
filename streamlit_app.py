import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BigBasket FMCG Gap Analyzer", layout="wide")

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
    st.error("Could not load CSVs. Make sure 'skus_enriched.csv' and 'cell_gap_scores.csv' are in the same folder as app.py.")
    st.stop()

# --------------------------
# Sidebar filters
# --------------------------
st.sidebar.title("Filters")

categories = sorted(cells["category"].unique())
selected_category = st.sidebar.selectbox("Category", options=categories)

subcats = sorted(cells.loc[cells["category"] == selected_category, "sub_category"].unique())
selected_subcat = st.sidebar.selectbox("Sub-Category", options=subcats)

gap_threshold = st.sidebar.slider("Whitespace threshold (Gap_Score)", min_value=0.5, max_value=0.95, value=0.7, step=0.05)

# --------------------------
# Header
# --------------------------
st.title("BigBasket FMCG Portfolio Gap Analyzer")
st.caption("Identify whitespace opportunities across Category × Sub-Category × Price Tier × Claims.")

# --------------------------
# KPI row
# --------------------------
subset_cat = cells[cells["category"] == selected_category].copy()
total_cells = len(subset_cat)
filled_cells = (subset_cat["Gap_Score"] > 0).sum()
coverage_pct = (filled_cells / total_cells * 100) if total_cells > 0 else 0
whitespace_count = (subset_cat["Gap_Score"] >= gap_threshold).sum()

col1, col2, col3 = st.columns(3)
col1.metric("Selected Category", selected_category)
col2.metric("Portfolio coverage %", f"{coverage_pct:.1f}%")
col3.metric(f"Whitespace (Gap ≥ {gap_threshold})", int(whitespace_count))

# --------------------------
# Heatmap
# --------------------------
heat_df = cells[(cells["category"] == selected_category) & (cells["sub_category"] == selected_subcat)].copy()
if heat_df.empty:
    st.warning("No data for the selected filters.")
else:
    pivot = heat_df.pivot_table(index="Claims", columns="Price_Tier", values="Gap_Score", aggfunc="max").fillna(0)
    fig_heat = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        aspect="auto",
        labels=dict(color="Gap Score"),
    )
    fig_heat.update_layout(title=f"Gap Score Heatmap — {selected_category} / {selected_subcat}")
    st.plotly_chart(fig_heat, use_container_width=True)

# --------------------------
# Top whitespace opportunities
# --------------------------
st.subheader("Top whitespace opportunities")
top_n = st.slider("Show top N", min_value=5, max_value=30, value=10, step=5)
top_gaps = cells[cells["Gap_Score"] >= gap_threshold].sort_values("Gap_Score", ascending=False).head(top_n)

if top_gaps.empty:
    st.info("No cells exceed the selected whitespace threshold.")
else:
    st.dataframe(
        top_gaps[["category", "sub_category", "Price_Tier", "Claims", "SKU_Count", "Gap_Score"]],
        use_container_width=True
    )

# --------------------------
# SKU explorer
# --------------------------
st.subheader("SKU explorer")
if {"product", "brand", "Price_Tier", "Claims"}.issubset(skus.columns):
    sku_view = skus[
        (skus["category"] == selected_category) &
        (skus["sub_category"] == selected_subcat)
    ]
    show_cols = [c for c in ["product", "brand", "sale_price", "market_price", "Price_Tier", "Claims", "Gap_Score", "p_url"] if c in sku_view.columns]
    st.dataframe(sku_view[show_cols].sort_values("Gap_Score", ascending=False), use_container_width=True)
else:
    st.info("SKU table missing some expected columns. The heatmap and whitespace table still work.")