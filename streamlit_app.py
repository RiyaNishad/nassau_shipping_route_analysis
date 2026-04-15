from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Nassau Candy | Intelligence Ultra",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .main { background-color: #0f172a; font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #374151 !important;
        color: #f3f4f6 !important;
        border: 1px solid #4b5563;
    }

    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .metric-label {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 26px;
        font-weight: 700;
        margin-top: 8px;
    }

    .stTabs [aria-selected="true"] {
        color: #fcd34d !important;
        border-bottom-color: #fcd34d !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    base_dir = Path(__file__).parent
    path = base_dir / "Nassau-Candy-Distributor.csv"

    if not path.exists():
        st.error(f"CSV file not found: {path}")
        st.stop()

    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce", dayfirst=True)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce", dayfirst=True)
    df["Lead_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

    for col in ["Sales", "Units", "Gross Profit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    state_map = {
        "California": "CA",
        "Texas": "TX",
        "New York": "NY",
        "Florida": "FL",
        "Illinois": "IL"
    }

    df["State_Code"] = df["State/Province"].map(state_map).fillna("")
    return df

df = load_data()

with st.sidebar:
    st.image("https://www.nassaucandy.com/skin/frontend/enterprise/nassaucandy/images/logo.png", use_container_width=True)
    st.markdown("### Control Panel")

    region_options = sorted(df["Region"].dropna().unique().tolist())
    product_options = sorted(df["Product Name"].dropna().unique().tolist())
    ship_options = sorted(df["Ship Mode"].dropna().unique().tolist())

    sel_regions = st.multiselect(
        "Region",
        region_options,
        default=region_options,
        key="ux_reg_f"
    )

    sel_prods = st.multiselect(
        "Products",
        product_options,
        default=[],
        key="ux_prod_f"
    )

    sel_ship = st.multiselect(
        "Ship Mode",
        ship_options,
        default=ship_options,
        key="ux_ship_f"
    )

    l_max = int(df["Lead_Days"].dropna().max()) if not df["Lead_Days"].dropna().empty else 100
    l_range = st.slider("Lead Time Filter", 0, l_max, (0, l_max), key="ux_lead_f")

mask = df["Region"].isin(sel_regions) & df["Ship Mode"].isin(sel_ship)

if sel_prods:
    mask &= df["Product Name"].isin(sel_prods)

filtered = df[mask].copy()
filtered = filtered[
    (filtered["Lead_Days"].fillna(0) >= l_range[0]) &
    (filtered["Lead_Days"].fillna(0) <= l_range[1])
]

st.title("Strategic Route Intelligence")

k1, k2, k3, k4, k5, k6 = st.columns(6)

sales_val = filtered["Sales"].sum(skipna=True)
profit_val = filtered["Gross Profit"].sum(skipna=True)
margin_val = (profit_val / sales_val * 100) if sales_val > 0 else 0
late_val = len(filtered[filtered["Lead_Days"] > 7])
avg_lead = filtered["Lead_Days"].mean(skipna=True)
status_val = "Optimal" if margin_val > 20 else "Review"

with k1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Sales</div><div class="metric-value">${sales_val:,.0f}</div></div>',
        unsafe_allow_html=True
    )
with k2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Profit</div><div class="metric-value">${profit_val:,.0f}</div></div>',
        unsafe_allow_html=True
    )
with k3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Margin</div><div class="metric-value">{margin_val:.1f}%</div></div>',
        unsafe_allow_html=True
    )
with k4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Late Orders</div><div class="metric-value" style="color:#ef4444;">{late_val:,}</div></div>',
        unsafe_allow_html=True
    )
with k5:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Avg Lead</div><div class="metric-value">{avg_lead:.1f}d</div></div>',
        unsafe_allow_html=True
    )
with k6:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Status</div><div class="metric-value">{status_val}</div></div>',
        unsafe_allow_html=True
    )

t1, t2, t3, t4, t5 = st.tabs(["🚀 Strategy", "🗺️ Routes", "📦 Products", "📊 Efficiency", "📑 Ledger"])
ACCENT = "#38bdf8"

with t1:
    st.subheader("Revenue vs. Profit Growth")
    trend = filtered.groupby("Order Date", as_index=False).agg({"Sales": "sum", "Gross Profit": "sum"})
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend["Order Date"], y=trend["Sales"], name="Sales",
        line=dict(color=ACCENT), fill="tozeroy"
    ))
    fig_trend.add_trace(go.Scatter(
        x=trend["Order Date"], y=trend["Gross Profit"], name="Profit",
        line=dict(color="#fcd34d")
    ))
    fig_trend.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig_trend, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        region_sales = filtered.groupby("Region", as_index=False)["Sales"].sum()
        fig1 = px.bar(region_sales, x="Region", y="Sales", template="plotly_dark",
                      color_discrete_sequence=[ACCENT])
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        region_profit = filtered.groupby("Region", as_index=False)["Gross Profit"].sum()
        fig2 = px.pie(region_profit, names="Region", values="Gross Profit",
                      hole=0.5, template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

with t2:
    st.subheader("Route Lead-Time Intensity")
    m_data = filtered.groupby(["State_Code", "State/Province"], as_index=False).agg(
        Lead_Days=("Lead_Days", "mean")
    )
    m_data = m_data[m_data["State_Code"] != ""]
    if not m_data.empty:
        fig_map = px.choropleth(
            m_data,
            locations="State_Code",
            locationmode="USA-states",
            color="Lead_Days",
            scope="usa",
            template="plotly_dark",
            color_continuous_scale="YlOrRd"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No state data available for map display.")

with t3:
    st.subheader("Product Performance Hierarchy")
    if "Division" in filtered.columns:
        sun = filtered.dropna(subset=["Division", "Region"]).copy()
        if not sun.empty:
            st.plotly_chart(
                px.sunburst(sun, path=["Division", "Region"], values="Sales", template="plotly_dark"),
                use_container_width=True
            )

    prod_sales = filtered.groupby("Product Name", as_index=False)["Sales"].sum().nlargest(10, "Sales")
    fig_prod = px.bar(
        prod_sales,
        x="Sales",
        y="Product Name",
        orientation="h",
        template="plotly_dark",
        color_discrete_sequence=[ACCENT]
    )
    st.plotly_chart(fig_prod, use_container_width=True)

with t4:
    st.subheader("Efficiency Matrix: Lead Time vs Profit")
    fig_scatter = px.scatter(
        filtered,
        x="Lead_Days",
        y="Gross Profit",
        color="Ship Mode",
        size="Sales",
        template="plotly_dark"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with t5:
    st.subheader("Transaction Audit Ledger")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
