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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .main {
        background: linear-gradient(135deg, #020617 0%, #0f172a 45%, #111827 100%);
        font-family: 'Inter', sans-serif;
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 55%, #312e81 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
    }

    [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
        fill: white !important;
    }

    [data-baseweb="slider"] div[role="slider"] {
        background-color: #22c55e !important;
        border-color: #22c55e !important;
    }

    [data-baseweb="slider"] div[style*="background"] {
        background: #22c55e !important;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95));
        border: 1px solid rgba(59,130,246,0.25);
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.28);
    }

    .metric-label {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 800;
        margin-top: 8px;
    }

    .stTabs [aria-selected="true"] {
        color: #22c55e !important;
        border-bottom-color: #22c55e !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 10px 14px;
    }

    .stButton button {
        background: linear-gradient(90deg, #3b82f6, #22c55e);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 700;
    }

    .stSelectbox, .stMultiSelect, .stSlider {
        border-radius: 12px;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4 {
        color: #f8fafc;
    }

    .stDataFrame {
        background-color: rgba(15, 23, 42, 0.95);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent

    candidates = [
        current_dir / "Nassau Candy Distributor.csv",
        current_dir / "Nassau-Candy-Distributor.csv",
        parent_dir / "Nassau Candy Distributor.csv",
        parent_dir / "Nassau-Candy-Distributor.csv",
        Path.cwd() / "Nassau Candy Distributor.csv",
        Path.cwd() / "Nassau-Candy-Distributor.csv",
    ]

    path = next((p for p in candidates if p.exists()), None)

    if path is None:
        st.error("CSV file not found in app folder, parent folder, or current working directory.")
        st.stop()

    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce", dayfirst=True)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce", dayfirst=True)
    df["Lead_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

    for col in ["Sales", "Units", "Gross Profit", "Cost"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "State/Province" in df.columns:
        state_map = {
            "California": "CA",
            "Texas": "TX",
            "New York": "NY",
            "Florida": "FL",
            "Illinois": "IL",
            "Pennsylvania": "PA",
            "Washington": "WA",
            "Ohio": "OH",
            "Georgia": "GA",
            "Michigan": "MI",
            "North Carolina": "NC",
            "Virginia": "VA",
            "Arizona": "AZ",
            "Louisiana": "LA",
            "Colorado": "CO",
            "Oregon": "OR",
            "Wisconsin": "WI",
            "Massachusetts": "MA",
            "New Jersey": "NJ",
            "Tennessee": "TN",
            "Maryland": "MD",
            "Indiana": "IN",
            "Missouri": "MO",
            "Minnesota": "MN",
            "Connecticut": "CT",
            "Kentucky": "KY",
            "Alabama": "AL",
            "South Carolina": "SC",
            "Oklahoma": "OK",
            "Kansas": "KS",
            "Utah": "UT",
            "Nevada": "NV",
            "Idaho": "ID",
            "Iowa": "IA",
            "Arkansas": "AR",
            "Mississippi": "MS",
            "Delaware": "DE",
            "Maine": "ME",
            "New Hampshire": "NH",
            "Rhode Island": "RI",
            "Vermont": "VT",
            "West Virginia": "WV",
            "Nebraska": "NE",
            "New Mexico": "NM",
            "Montana": "MT",
            "North Dakota": "ND",
            "South Dakota": "SD",
            "Wyoming": "WY",
        }
        df["State_Code"] = df["State/Province"].map(state_map).fillna("")
    else:
        df["State_Code"] = ""

    return df

df = load_data()

with st.sidebar:
    st.markdown("### Control Panel")

    region_options = sorted(df["Region"].dropna().unique().tolist()) if "Region" in df.columns else []
    ship_options = sorted(df["Ship Mode"].dropna().unique().tolist()) if "Ship Mode" in df.columns else []
    product_options = sorted(df["Product Name"].dropna().unique().tolist()) if "Product Name" in df.columns else []

    sel_regions = st.multiselect("Region", region_options, default=region_options, key="ux_reg_f")
    sel_ship = st.multiselect("Ship Mode", ship_options, default=ship_options, key="ux_ship_f")
    sel_prods = st.multiselect("Products", product_options, default=[], key="ux_prod_f")

    l_max = int(df["Lead_Days"].dropna().max()) if not df["Lead_Days"].dropna().empty else 30
    l_range = st.slider("Lead Time Filter", 0, l_max, (0, l_max), key="ux_lead_f")

mask = pd.Series(True, index=df.index)

if "Region" in df.columns and sel_regions:
    mask &= df["Region"].isin(sel_regions)

if "Ship Mode" in df.columns and sel_ship:
    mask &= df["Ship Mode"].isin(sel_ship)

if sel_prods and "Product Name" in df.columns:
    mask &= df["Product Name"].isin(sel_prods)

filtered = df[mask].copy()
filtered = filtered[
    filtered["Lead_Days"].fillna(0).between(l_range[0], l_range[1])
]

st.title("Strategic Route Intelligence")

k1, k2, k3, k4, k5, k6 = st.columns(6)

sales_val = filtered["Sales"].sum(skipna=True) if "Sales" in filtered.columns else 0
profit_val = filtered["Gross Profit"].sum(skipna=True) if "Gross Profit" in filtered.columns else 0
margin_val = (profit_val / sales_val * 100) if sales_val > 0 else 0
late_val = int((filtered["Lead_Days"] > 7).sum()) if "Lead_Days" in filtered.columns else 0
avg_lead = filtered["Lead_Days"].mean(skipna=True) if "Lead_Days" in filtered.columns else np.nan
status_val = "Optimal" if margin_val > 20 else "Review"

metric_html = lambda label, value, extra="": f'''
<div class="metric-card">
    <div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div>
    {extra}
</div>
'''

with k1:
    st.markdown(metric_html("Sales", f"${sales_val:,.0f}"), unsafe_allow_html=True)
with k2:
    st.markdown(metric_html("Profit", f"${profit_val:,.0f}"), unsafe_allow_html=True)
with k3:
    st.markdown(metric_html("Margin", f"{margin_val:.1f}%"), unsafe_allow_html=True)
with k4:
    st.markdown(metric_html("Late Orders", f"{late_val:,}", '<div class="metric-label" style="color:#ef4444;">> 7 lead days</div>'), unsafe_allow_html=True)
with k5:
    st.markdown(metric_html("Avg Lead", f"{avg_lead:.1f}d" if pd.notna(avg_lead) else "N/A"), unsafe_allow_html=True)
with k6:
    st.markdown(metric_html("Status", status_val), unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs(["🚀 Strategy", "🗺️ Routes", "📦 Products", "📊 Efficiency", "📑 Ledger"])
ACCENT = "#38bdf8"

with t1:
    st.subheader("Revenue vs. Profit Growth")
    if "Order Date" in filtered.columns and "Sales" in filtered.columns and "Gross Profit" in filtered.columns:
        trend = filtered.groupby("Order Date", as_index=False).agg({"Sales": "sum", "Gross Profit": "sum"})
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=trend["Order Date"], y=trend["Sales"], name="Sales", line=dict(color=ACCENT), fill="tozeroy"))
        fig_trend.add_trace(go.Scatter(x=trend["Order Date"], y=trend["Gross Profit"], name="Profit", line=dict(color="#fcd34d")))
        fig_trend.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if "Region" in filtered.columns and "Sales" in filtered.columns:
            region_sales = filtered.groupby("Region", as_index=False)["Sales"].sum()
            st.plotly_chart(px.bar(region_sales, x="Region", y="Sales", template="plotly_dark", color_discrete_sequence=[ACCENT]), use_container_width=True)
    with c2:
        if "Region" in filtered.columns and "Gross Profit" in filtered.columns:
            region_profit = filtered.groupby("Region", as_index=False)["Gross Profit"].sum()
            st.plotly_chart(px.pie(region_profit, names="Region", values="Gross Profit", hole=0.5, template="plotly_dark"), use_container_width=True)

with t2:
    st.subheader("Route Lead-Time Intensity")

    if "State_Code" in filtered.columns:
        map_data = filtered.groupby(["State_Code", "State/Province"], as_index=False).agg(
            Lead_Days=("Lead_Days", "mean"),
            Sales=("Sales", "sum"),
            Orders=("Order Date", "count")
        )
        map_data = map_data[map_data["State_Code"] != ""]

        if not map_data.empty:
            fig_map = px.choropleth(
                map_data,
                locations="State_Code",
                locationmode="USA-states",
                color="Lead_Days",
                scope="usa",
                hover_name="State/Province",
                hover_data={
                    "State_Code": False,
                    "Lead_Days": ":.1f",
                    "Sales": ":,.2f",
                    "Orders": True
                },
                color_continuous_scale=["#e0f2fe", "#7dd3fc", "#38bdf8", "#0ea5e9", "#0369a1"],
            )

            fig_map.update_traces(
                marker_line_color="white",
                marker_line_width=1.1
            )

            fig_map.update_layout(
                template="plotly_dark",
                height=600,
                margin=dict(l=10, r=10, t=20, b=10),
                geo=dict(
                    bgcolor="rgba(0,0,0,0)",
                    lakecolor="rgba(0,0,0,0)",
                    showlakes=True,
                    showland=True,
                    landcolor="#0f172a",
                    subunitcolor="white",
                    countrycolor="white"
                )
            )

            st.plotly_chart(fig_map, use_container_width=True)
            fig_map.update_layout(
    title=dict(
        text="Route Lead-Time Intensity by State",
        x=0.5,
        xanchor="center",
        y=0.95,
        font=dict(size=24, color="#f8fafc")
    ),
    annotations=[
        dict(
            text="Average lead days across states",
            x=0.5,
            y=1.02,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=13, color="#94a3b8")
        )
    ]
)

with t3:
    st.subheader("Product Performance Hierarchy")
    if "Division" in filtered.columns and "Region" in filtered.columns and "Sales" in filtered.columns:
        sun = filtered.dropna(subset=["Division", "Region"]).copy()
        if not sun.empty:
            st.plotly_chart(px.sunburst(sun, path=["Division", "Region"], values="Sales", template="plotly_dark"), use_container_width=True)

    if "Product Name" in filtered.columns and "Sales" in filtered.columns:
        prod_sales = filtered.groupby("Product Name", as_index=False)["Sales"].sum().nlargest(10, "Sales")
        st.plotly_chart(
            px.bar(prod_sales, x="Sales", y="Product Name", orientation="h", template="plotly_dark", color_discrete_sequence=[ACCENT]),
            use_container_width=True
        )

with t4:
    st.subheader("Efficiency Matrix: Lead Time vs Profit")
    if "Lead_Days" in filtered.columns and "Gross Profit" in filtered.columns:
        st.plotly_chart(
            px.scatter(filtered, x="Lead_Days", y="Gross Profit", color="Ship Mode", size="Sales", template="plotly_dark"),
            use_container_width=True
        )

with t5:
    st.subheader("Transaction Audit Ledger")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
