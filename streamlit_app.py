import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Nassau Candy | Intelligence Ultra", page_icon="🎯", layout="wide")

# --- 2. THE CSS (Deep Midnight Sidebar & High-End Cards) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .main { background-color: #0f172a; font-family: 'Inter', sans-serif; }
    
    /* Deep Midnight Sidebar Reset */
    [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1f2937; }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #374151 !important;
        color: #f3f4f6 !important;
        border: 1px solid #4b5563;
    }

    /* Professional Metric Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-label { color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; }
    .metric-value { color: #f8fafc; font-size: 26px; font-weight: 700; margin-top: 8px; }
    
    .stTabs [aria-selected="true"] { color: #fcd34d !important; border-bottom-color: #fcd34d !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    path = r"C:\Users\riyan\OneDrive\Attachments\Nassau Candy Distributor.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce', dayfirst=True)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors='coerce', dayfirst=True)
    df["Lead_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    for col in ["Sales", "Units", "Gross Profit"]:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
    
    state_map = {"California": "CA", "Texas": "TX", "New York": "NY", "Florida": "FL", "Illinois": "IL"}
    df["State_Code"] = df["State/Province"].map(state_map).fillna(df["State/Province"])
    return df

df = load_data()

# --- 4. SIDEBAR (ALL FILTERS + UNIQUE KEYS) ---
with st.sidebar:
    st.image("https://www.nassaucandy.com/skin/frontend/enterprise/nassaucandy/images/logo.png", use_container_width=True)
    st.markdown("### Control Panel")
    sel_regions = st.multiselect("Region", sorted(df["Region"].unique()), default=df["Region"].unique(), key="ux_reg_f")
    sel_prods = st.multiselect("Products", sorted(df["Product Name"].unique()[:100]), key="ux_prod_f")
    sel_ship = st.multiselect("Ship Mode", sorted(df["Ship Mode"].unique()), default=df["Ship Mode"].unique(), key="ux_ship_f")
    
    l_max = int(df["Lead_Days"].max()) if not df["Lead_Days"].isna().all() else 100
    l_range = st.slider("Lead Time Filter", 0, l_max, (0, l_max), key="ux_lead_f")

# --- 5. FILTERING ---
mask = (df["Region"].isin(sel_regions)) & (df["Ship Mode"].isin(sel_ship))
if sel_prods: mask &= (df["Product Name"].isin(sel_prods))
filtered = df[mask]
filtered = filtered[(filtered["Lead_Days"] >= l_range[0]) & (filtered["Lead_Days"] <= l_range[1])]

# --- 6. ALL 6 KPIs (RESTORED) ---
st.title("Strategic Route Intelligence")
k1, k2, k3, k4, k5, k6 = st.columns(6)
sales_val = filtered['Sales'].sum()
profit_val = filtered['Gross Profit'].sum()
margin_val = (profit_val / sales_val * 100) if sales_val > 0 else 0
late_val = len(filtered[filtered['Lead_Days'] > 7])

with k1: st.markdown(f'<div class="metric-card"><div class="metric-label">Sales</div><div class="metric-value">${sales_val:,.0f}</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="metric-card"><div class="metric-label">Profit</div><div class="metric-value">${profit_val:,.0f}</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="metric-card"><div class="metric-label">Margin</div><div class="metric-value">{margin_val:.1f}%</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="metric-card"><div class="metric-label">Late Orders</div><div class="metric-value" style="color:#ef4444;">{late_val:,}</div></div>', unsafe_allow_html=True)
with k5: st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Lead</div><div class="metric-value">{filtered["Lead_Days"].mean():.1f}d</div></div>', unsafe_allow_html=True)
with k6: st.markdown(f'<div class="metric-card"><div class="metric-label">Status</div><div class="metric-value">{"Optimal" if margin_val > 20 else "Review"}</div></div>', unsafe_allow_html=True)

# --- 7. ALL 5 TABS (RESTORED) ---
t1, t2, t3, t4, t5 = st.tabs(["🚀 Strategy", "🗺️ Routes", "📦 Products", "📊 Efficiency", "📑 Ledger"])

ACCENT = "#38bdf8"

with t1:
    st.subheader("Revenue vs. Profit Growth")
    trend = filtered.groupby("Order Date").agg({"Sales": "sum", "Gross Profit": "sum"}).reset_index()
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=trend["Order Date"], y=trend["Sales"], name="Sales", line=dict(color=ACCENT), fill='tozeroy'))
    fig_trend.add_trace(go.Scatter(x=trend["Order Date"], y=trend["Gross Profit"], name="Profit", line=dict(color="#fcd34d")))
    fig_trend.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig_trend, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(px.bar(filtered.groupby("Region")["Sales"].sum().reset_index(), x="Region", y="Sales", template="plotly_dark", color_discrete_sequence=[ACCENT]), use_container_width=True)
    with c2: st.plotly_chart(px.pie(filtered.groupby("Region")["Gross Profit"].sum().reset_index(), names="Region", values="Gross Profit", hole=0.5, template="plotly_dark"), use_container_width=True)

with t2:
    st.subheader("Route Lead-Time Intensity")
    m_data = filtered.groupby(["State_Code", "State/Province"]).agg({"Lead_Days": "mean"}).reset_index()
    st.plotly_chart(px.choropleth(m_data, locations="State_Code", locationmode="USA-states", color="Lead_Days", scope="usa", template="plotly_dark", color_continuous_scale="YlOrRd"), use_container_width=True)

with t3:
    st.subheader("Product Performance Hierarchy")
    if "Division" in filtered.columns:
        st.plotly_chart(px.sunburst(filtered, path=['Division', 'Region'], values='Sales', template="plotly_dark"), use_container_width=True)
    st.plotly_chart(px.bar(filtered.groupby("Product Name")["Sales"].sum().nlargest(10).reset_index(), x="Sales", y="Product Name", orientation='h', template="plotly_dark", color_discrete_sequence=[ACCENT]), use_container_width=True)

with t4:
    st.subheader("Efficiency Matrix: Mode vs. Margin")
    st.plotly_chart(px.scatter(filtered, x="Lead_Days", y="Gross Profit", color="Ship Mode", size="Sales", template="plotly_dark"), use_container_width=True)

with t5:
    st.subheader("Transaction Audit Ledger")
    st.dataframe(filtered, use_container_width=True)