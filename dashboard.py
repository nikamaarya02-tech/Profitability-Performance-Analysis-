import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

#python -m streamlit run dashboard.py
# =========================
# COLOR PALETTE
# =========================

PRIMARY = "#8B5CF6"   # Purple
SUCCESS = "#22C55E"   # Green
WARNING = "#F59E0B"   # Orange
DANGER = "#EF4444"    # Red
INFO = "#38BDF8"      # Blue

# ==================================================
# DEBUG INFO
# ==================================================

st.write("Current Working Directory:")
st.write(os.getcwd())

st.write("Files Available:")
st.write(os.listdir())

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Profitability & Margin Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.stApp {
    background-color: #0F172A;
    color: white;
}

section[data-testid="stSidebar"]{
    background-color: #111827;
}

div[data-testid="metric-container"]{
    background-color:#1E293B;
    border:1px solid #334155;
    padding:15px;
    border-radius:12px;
}

h1,h2,h3{
    color:white !important;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():

    df = pd.read_csv("Nassau Candy Distributor.csv")

    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        dayfirst=True,
        errors="coerce"
    )

    df["Margin %"] = np.where(
        df["Sales"] > 0,
        (df["Gross Profit"] / df["Sales"]) * 100,
        0
    )

    df["Profit Per Unit"] = np.where(
        df["Units"] > 0,
        df["Gross Profit"] / df["Units"],
        0
    )

    return df


df = load_data()

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("📌 Filters")

min_date = df["Order Date"].min()
max_date = df["Order Date"].max()

date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date]
)

division_list = sorted(df["Division"].dropna().unique())

division = st.sidebar.selectbox(
    "Division",
    ["All"] + division_list
)

if "Region" in df.columns:

    region_list = sorted(df["Region"].dropna().unique())

    region = st.sidebar.selectbox(
        "Region",
        ["All"] + region_list
    )

else:
    region = "All"

margin_threshold = st.sidebar.slider(
    "Margin Threshold (%)",
    0,
    100,
    20
)

product_search = st.sidebar.selectbox(
    "Select Product",
    ["All"] + sorted(df["Product Name"].unique())
)

# ==================================================
# FILTER DATA
# ==================================================

filtered_df = df.copy()

if len(date_range) == 2:

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= pd.to_datetime(date_range[0]))
        &
        (filtered_df["Order Date"] <= pd.to_datetime(date_range[1]))
    ]

if division != "All":

    filtered_df = filtered_df[
        filtered_df["Division"] == division
    ]

if region != "All":

    filtered_df = filtered_df[
        filtered_df["Region"] == region
    ]

filtered_df = filtered_df[
    filtered_df["Margin %"] >= margin_threshold
]

search_df = filtered_df.copy()

if product_search != "All":

    search_df = search_df[
        search_df["Product Name"] == product_search
    ]

# ==================================================
# HEADER
# ==================================================

st.title("📈 Profitability & Margin Analysis Dashboard")

st.markdown(
    "Comprehensive overview of product profitability, division performance, and margin diagnostics."
)

# ==================================================
# KPI CARDS
# ==================================================

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
avg_margin = filtered_df["Margin %"].mean()
total_products = filtered_df["Product Name"].nunique()
total_orders = filtered_df["Order ID"].nunique()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Sales", f"${total_sales:,.2f}")
c2.metric("Total Gross Profit", f"${total_profit:,.2f}")
c3.metric("Average Margin %", f"{avg_margin:.2f}%")
c4.metric("Total Products", total_products)
c5.metric("Total Orders", total_orders)

# ==================================================
# PRODUCT SUMMARY
# ==================================================

product_summary = (
   search_df
    .groupby("Product Name")
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum",
        "Units": "sum"
    })
    .reset_index()
)

product_summary["Margin %"] = (
    product_summary["Gross Profit"]
    /
    product_summary["Sales"]
) * 100

product_summary["Profit Per Unit"] = (
    product_summary["Gross Profit"]
    /
    product_summary["Units"]
)

# ==================================================
# PRODUCT PROFITABILITY OVERVIEW
# ==================================================

st.markdown("---")
st.header("1️⃣ Product Profitability Overview")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Product Margin Leaderboard")

    leaderboard = product_summary.sort_values(
        "Margin %",
        ascending=False
    ).head(10)

    st.dataframe(
        leaderboard[
            [
                "Product Name",
                "Sales",
                "Gross Profit",
                "Margin %"
            ]
        ],
        use_container_width=True
    )

with col2:

    st.subheader("Profit Contribution by Product")

    top_products = product_summary.nlargest(
        10,
        "Gross Profit"
    )

    fig = px.pie(
    top_products,
    names="Product Name",
    values="Gross Profit",
    hole=0.60,
    color_discrete_sequence=[
        "#60A5FA",
        "#22C55E",
        "#F59E0B",
        "#EF4444",
        "#8B5CF6",
        "#EC4899",
        "#14B8A6",
        "#F97316"
    ]
)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# SALES VS PROFIT
# ==================================================

st.subheader("Sales vs Gross Profit by Product")

top_sales = product_summary.nlargest(
    10,
    "Sales"
)

fig = px.bar(
    top_sales,
    x="Product Name",
    y=["Sales", "Gross Profit"],
    barmode="group",
    color_discrete_sequence=[
        PRIMARY,
        SUCCESS
    ]
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# TOP PRODUCTS BY PROFIT
# ==================================================

col1, col2 = st.columns(2)

with col1:

    top_profit = product_summary.nlargest(
        10,
        "Gross Profit"
    )

    fig = px.bar(
    top_profit,
    x="Product Name",
    y="Gross Profit",
    title="Top 10 Products by Gross Profit",
    color_discrete_sequence=[SUCCESS]
)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.histogram(
    product_summary,
    x="Margin %",
    nbins=10,
    title="Margin Distribution",
    color_discrete_sequence=[PRIMARY]
)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# DIVISION DASHBOARD
# ==================================================

st.markdown("---")
st.header("2️⃣ Division Performance Dashboard")

division_summary = (
    filtered_df
    .groupby("Division")
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum"
    })
    .reset_index()
)

division_summary["Margin %"] = (
    division_summary["Gross Profit"]
    /
    division_summary["Sales"]
) * 100

c1, c2 = st.columns(2)

with c1:

    fig = px.bar(
    division_summary,
    x="Division",
    y=["Sales", "Gross Profit"],
    barmode="group",
    title="Revenue vs Profit Comparison",
    color_discrete_sequence=[
        PRIMARY,
        SUCCESS
    ]
)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with c2:

    fig = px.bar(
    division_summary,
    x="Division",
    y="Margin %",
    title="Margin Distribution by Division",
    color_discrete_sequence=[WARNING]
)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# COST VS MARGIN DIAGNOSTICS
# ==================================================

st.markdown("---")
st.header("3️⃣ Cost vs Margin Diagnostics")

if "Cost" not in filtered_df.columns:
    filtered_df["Cost"] = (
        filtered_df["Sales"]
        - filtered_df["Gross Profit"]
    )

avg_cost = filtered_df["Cost"].mean()
avg_margin = filtered_df["Margin %"].mean()

fig = px.scatter(
    filtered_df,
    x="Cost",
    y="Margin %",
    size="Sales",
    color="Division",
    hover_name="Product Name",
    title="Product Cost vs Margin Analysis",
    color_discrete_sequence=[
        PRIMARY,
        SUCCESS,
        WARNING,
        DANGER,
        INFO
    ]
)

fig.add_vline(
    x=avg_cost,
    line_dash="dash",
    line_color="white"
)

fig.add_hline(
    y=avg_margin,
    line_dash="dash",
    line_color="white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.info("""
⭐ High Margin + Low Cost = Best Products

🟢 High Margin + High Cost = Premium Products

🟡 Low Margin + Low Cost = Average Products

🔴 Low Margin + High Cost = Risk Products
""")

col1, col2 = st.columns(2)

with col1:

    low_margin = product_summary.sort_values(
        "Margin %",
        ascending=True
    ).head(10)

    fig = px.bar(
        low_margin,
        x="Product Name",
        y="Margin %",
        title="Lowest Margin Products",
        color="Margin %",
        color_continuous_scale=[
            "#EF4444",
            "#F59E0B",
            "#22C55E"
        ]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    st.subheader("Margin Risk Flags")

    risk_products = product_summary[
        product_summary["Margin %"] < 30
    ]

    st.dataframe(
        risk_products.sort_values(
            "Margin %",
            ascending=True
        ),
        use_container_width=True
    )

# ==================================================
# PARETO ANALYSIS
# ==================================================

st.markdown("---")
st.header("4️⃣ Profit Concentration Analysis")

pareto = product_summary.sort_values(
    "Gross Profit",
    ascending=False
)

pareto["Cum Profit"] = (
    pareto["Gross Profit"]
    .cumsum()
)

pareto["Cum %"] = (
    pareto["Cum Profit"]
    /
    pareto["Gross Profit"].sum()
) * 100

fig = go.Figure()

fig.add_trace(
    go.Bar(
    x=pareto["Product Name"],
    y=pareto["Gross Profit"],
    name="Gross Profit",
    marker_color=PRIMARY
)
)

fig.add_trace(
    go.Scatter(
    x=pareto["Product Name"],
    y=pareto["Cum %"],
    mode="lines+markers",
    name="Cumulative %",
    yaxis="y2",
    line=dict(
        color=SUCCESS,
        width=4
    )
)
)

fig.update_layout(
    title="Pareto Chart",
    yaxis=dict(title="Gross Profit"),
    yaxis2=dict(
        title="Cumulative %",
        overlaying="y",
        side="right"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

top5_profit = pareto.head(5)["Gross Profit"].sum()

dependency = (
    top5_profit
    /
    pareto["Gross Profit"].sum()
) * 100

st.metric(
    "Top 5 Product Dependency",
    f"{dependency:.2f}%"
)

st.success("Dashboard Loaded Successfully")