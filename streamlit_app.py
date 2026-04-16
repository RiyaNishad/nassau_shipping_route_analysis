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
        background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 45%, #fdfdff 100%);
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #dbeafe 0%, #bfdbfe 45%, #eff6ff 100%) !important;
        border-right: 1px solid #cbd5e1;
    }

    [data-testid="stSidebar"] * {
        color: #0f172a !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #60a5fa !important;
        color: white !important;
        border: none !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] svg {
        fill: white !important;
    }

    [data-baseweb="slider"] div[role="slider"] {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
    }

    [data-baseweb="slider"] div[style*="background"] {
        background: #3b82f6 !important;
    }

    .metric-card {
        background: linear-gradient(180deg, #ffffff, #f8fbff);
        border: 1px solid #dbeafe;
        padding: 1.2rem;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(59,130,246,0.08);
    }

    .metric-label {
        color: #64748b;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    .metric-value {
        color: #0f172a;
        font-size: 28px;
        font-weight: 800;
        margin-top: 8px;
    }

    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.9);
        border-radius: 12px;
        padding: 10px 14px;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4 {
        color: #0f172a;
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

    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce", dayfirst=True)
    if "Ship Date" in df.columns:
        df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce", dayfirst=True)

    if "Order Date" in df.columns and "Ship Date" in df.columns:
        df["Lead_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    else:
        df["Lead_Days"] = np.nan

    for col in ["Sales", "Units", "Gross Profit", "Cost"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "State/Province" in df.columns:
        state_map = {
            "California": "CA", "Texas": "TX", "New York": "NY", "Florida": "FL",
            "Illinois": "IL", "Pennsylvania": "PA", "Washington": "WA", "Ohio": "OH",
            "Georgia": "GA", "Michigan": "MI", "North Carolina": "NC", "Virginia": "VA",
            "Arizona": "AZ", "Louisiana": "LA", "Colorado": "CO", "Oregon": "OR",
            "Wisconsin": "WI", "Massachusetts": "MA", "New Jersey": "NJ", "Tennessee": "TN",
            "Maryland": "MD", "Indiana": "IN", "Missouri": "MO", "Minnesota": "MN",
            "Connecticut": "CT", "Kentucky": "KY", "Alabama": "AL", "South Carolina": "SC",
            "Oklahoma": "OK", "Kansas": "KS", "Utah": "UT", "Nevada": "NV",
            "Idaho": "ID", "Iowa": "IA", "Arkansas": "AR", "Mississippi": "MS",
            "Delaware": "DE", "Maine": "ME", "New Hampshire": "NH", "Rhode Island": "RI",
            "Vermont": "VT", "West Virginia": "WV", "Nebraska": "NE", "New Mexico": "NM",
            "Montana": "MT", "North Dakota": "ND", "South Dakota": "SD", "Wyoming": "WY"
        }
        df["State_Code"] = df["State/Province"].map(state_map).fillna("")
    else:
        df["State_Code"] = ""

    return df

df = load_data()

st.title("Strategic Route Intelligence")

order_id_input = st.text_input("Enter Customer Order ID", placeholder="Type Order ID here...")

if order_id_input.strip():
    if "Order ID" in df.columns:
        filtered = df[df["Order ID"].astype(str).str.contains(order_id_input.strip(), case=False, na=False)].copy()
    else:
        st.error("Order ID column not found in dataset.")
        st.stop()
else:
    filtered = df.copy()

if filtered.empty:
    st.warning("No records found for this Order ID.")
    st.stop()

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

mask = pd.Series(True, index=filtered.index)

if "Region" in filtered.columns and sel_regions:
    mask &= filtered["Region"].isin(sel_regions)

if "Ship Mode" in filtered.columns and sel_ship:
    mask &= filtered["Ship Mode"].isin(sel_ship)

if sel_prods and "Product Name" in filtered.columns:
    mask &= filtered["Product Name"].isin(sel_prods)

filtered = filtered[mask].copy()
filtered = filtered[filtered["Lead_Days"].fillna(0).between(l_range[0], l_range[1])]

if filtered.empty:
    st.warning("No records match the current filters.")
    st.stop()

k1, k2, k3, k4, k5, k6 = st.columns(6)

sales_val = filtered["Sales"].sum(skipna=True) if "Sales" in filtered.columns else 0
profit_val = filtered["Gross Profit"].sum(skipna=True) if "Gross Profit" in filtered.columns else 0
margin_val = (profit_val / sales_val * 100) if sales_val > 0 else 0
late_val = int((filtered["Lead_Days"] > 7).sum()) if "Lead_Days" in filtered.columns else 0
avg_lead = filtered["Lead_Days"].mean(skipna=True) if "Lead_Days" in filtered.columns else np.nan
status_val = "Optimal" if margin_val > 20 else "Review"

metric_html = lambda label, value: f'''
<div class="metric-card">
    <div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div>
</div>
'''

with k1:
    st.markdown(metric_html("Sales", f"${sales_val:,.0f}"), unsafe_allow_html=True)
with k2:
    st.markdown(metric_html("Profit", f"${profit_val:,.0f}"), unsafe_allow_html=True)
with k3:
    st.markdown(metric_html("Margin", f"{margin_val:.1f}%"), unsafe_allow_html=True)
with k4:
    st.markdown(metric_html("Late Orders", f"{late_val:,}"), unsafe_allow_html=True)
with k5:
    st.markdown(metric_html("Avg Lead", f"{avg_lead:.1f}d" if pd.notna(avg_lead) else "N/A"), unsafe_allow_html=True)
with k6:
    st.markdown(metric_html("Status", status_val), unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "🗺️ Routes", "📦 Products", "📑 Ledger"])
ACCENT = "#3b82f6"
GOLD = "#f59e0b"
TEAL = "#14b8a6"

with t1:
    st.subheader("Revenue vs Profit Growth")
    if "Order Date" in filtered.columns and "Sales" in filtered.columns and "Gross Profit" in filtered.columns:
        trend = filtered.groupby("Order Date", as_index=False).agg({"Sales": "sum", "Gross Profit": "sum"})
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=trend["Order Date"], y=trend["Sales"], name="Sales", line=dict(color=ACCENT), fill="tozeroy"))
        fig_trend.add_trace(go.Scatter(x=trend["Order Date"], y=trend["Gross Profit"], name="Profit", line=dict(color=GOLD)))
        fig_trend.update_layout(template="plotly_white", height=350, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_trend, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if "Region" in filtered.columns and "Sales" in filtered.columns:
            region_sales = filtered.groupby("Region", as_index=False)["Sales"].sum()
            st.plotly_chart(
                px.bar(region_sales, x="Region", y="Sales", template="plotly_white", color_discrete_sequence=[ACCENT]),
                use_container_width=True
            )
    with c2:
        if "Region" in filtered.columns and "Gross Profit" in filtered.columns:
            region_profit = filtered.groupby("Region", as_index=False)["Gross Profit"].sum()
            st.plotly_chart(
                px.pie(region_profit, names="Region", values="Gross Profit", hole=0.5, template="plotly_white",
                       color_discrete_sequence=[ACCENT, TEAL, GOLD, "#8b5cf6"]),
                use_container_width=True
            )

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
                color_continuous_scale=["#eff6ff", "#bfdbfe", "#60a5fa", "#3b82f6", "#1d4ed8"],
            )
            fig_map.update_traces(marker_line_color="white", marker_line_width=1.1)
            fig_map.update_layout(
                template="plotly_white",
                height=600,
                margin=dict(l=10, r=10, t=50, b=10),
                title=dict(text="Route Lead-Time Intensity by State", x=0.5, xanchor="center", font=dict(size=22, color="#0f172a")),
                annotations=[
                    dict(
                        text="Average lead days across states",
                        x=0.5,
                        y=1.04,
                        xref="paper",
                        yref="paper",
                        showarrow=False,
                        font=dict(size=13, color="#64748b")
                    )
                ],
                geo=dict(
                    bgcolor="rgba(0,0,0,0)",
                    lakecolor="rgba(0,0,0,0)",
                    showlakes=True,
                    showland=True,
                    landcolor="#f8fbff",
                    subunitcolor="#cbd5e1",
                    countrycolor="#cbd5e1"
                )
            )
            st.plotly_chart(fig_map, use_container_width=True)

with t3:
    st.subheader("Product Performance")
    if "Division" in filtered.columns and "Region" in filtered.columns and "Sales" in filtered.columns:
        sun = filtered.dropna(subset=["Division", "Region"]).copy()
        if not sun.empty:
            st.plotly_chart(
                px.sunburst(sun, path=["Division", "Region"], values="Sales", template="plotly_white"),
                use_container_width=True
            )

    if "Product Name" in filtered.columns and "Sales" in filtered.columns:
        prod_sales = filtered.groupby("Product Name", as_index=False)["Sales"].sum().nlargest(10, "Sales")
        st.plotly_chart(
            px.bar(prod_sales, x="Sales", y="Product Name", orientation="h", template="plotly_white", color_discrete_sequence=[ACCENT]),
            use_container_width=True
        )

with t4:
    st.subheader("Transaction Audit Ledger")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
