# MyProj
# Bullion Tracker & Valuer
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 1. PAGE CONFIG
st.set_page_config(page_title="Bullion Pro 2026", layout="wide", page_icon="📈")

# 2. DATA ENGINE
@st.cache_data
def get_final_data():
    years = list(range(1975, 2027))
    gold = [540, 630, 680, 720, 780, 1330, 1800, 1640, 1750, 2100, 2130, 2140, 2570, 3130, 3200, 3460, 3750, 4100, 4140, 4480, 4500, 4400, 4700, 4900, 5200, 5600, 6000, 6500, 7000, 7500, 8000, 8500, 9500, 10500, 12000, 14500, 18500, 26400, 31000, 29600, 28000, 26343, 27500, 29000, 31500, 35000, 38000, 48600, 52000, 60000, 80249, 94630]
    silver = [1170, 1350, 1450, 1550, 1650, 2715, 2680, 3105, 3570, 3955, 3920, 3800, 4500, 5500, 6400, 6800, 7200, 7500, 7600, 7800, 7900, 7870, 8500, 9000, 9500, 10000, 10500, 11000, 12000, 13000, 14000, 15000, 17000, 19000, 22000, 25000, 27200, 49000, 59000, 48000, 40000, 36318, 40000, 45000, 50000, 55000, 60000, 63000, 70000, 89130, 190000, 248900]
    return pd.DataFrame({"Year": years, "Gold": gold, "Silver": silver})

df = get_final_data()
LIVE_G, LIVE_S = 94630, 248900

# 3. SIDEBAR & TOOLS
st.sidebar.title("🛠️ Control Center")
mode = st.sidebar.selectbox("Feature", ["Market Trends", "Wealth Valuer"])

# CSV Download Utility
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

st.sidebar.download_button("📥 Export History to CSV", data=convert_df(df), file_name="bullion_history.csv", mime="text/csv")

# 4. MARKET TRENDS WITH PROJECTIONS
if mode == "Market Trends":
    st.header("📊 Market Insights & 2030 Projections")
    
    show_proj = st.checkbox("Show 2030 AI Projection (Based on 12% CAGR)", value=True)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Base Historical Data
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Gold'], name="Gold (Actual)", line=dict(color='#FFD700', width=4)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Silver'], name="Silver (Actual)", line=dict(color='#C0C0C0', width=4)), secondary_y=True)

    # 5. PROJECTION LOGIC
    if show_proj:
        proj_years = [2027, 2028, 2029, 2030]
        # CAGR formula: Final = Current * (1 + r)^n
        g_proj = [LIVE_G * (1.12**i) for i in range(1, 5)]
        s_proj = [LIVE_S * (1.15**i) for i in range(1, 5)]
        
        fig.add_trace(go.Scatter(x=proj_years, y=g_proj, name="Gold (Projected)", line=dict(color='#FFD700', dash='dot')), secondary_y=False)
        fig.add_trace(go.Scatter(x=proj_years, y=s_proj, name="Silver (Projected)", line=dict(color='#C0C0C0', dash='dot')), secondary_y=True)

    fig.update_layout(template="plotly_dark", hovermode="x unified", height=600, title="50-Year History + 4-Year Forecast")
    st.plotly_chart(fig, use_container_width=True)

# 6. WEALTH VALUER
else:
    st.header("⚖️ Private Wealth Calculator")
    col1, col2 = st.columns(2)
    with col1:
        metal = st.radio("Asset Type", ["Gold", "Silver"])
        weight = st.number_input("Total Weight (Grams)", min_value=0.0, value=100.0)
    with col2:
        buy_in = st.number_input("Avg Purchase Price", value=55000.0)
        st.write(f"**Current Rate:** ₹{LIVE_G if metal=='Gold' else LIVE_S:,.0f}")

    current_val = (weight / (10 if metal == "Gold" else 1000)) * (LIVE_G if metal == "Gold" else LIVE_S)
    invested = (weight / (10 if metal == "Gold" else 1000)) * buy_in
    profit = current_val - invested

    st.divider()
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Current Portfolio Value", f"₹{current_val:,.0f}")
    kpi2.metric("Total Profit", f"₹{profit:,.0f}", f"{(profit/invested*100):.1f}%" if invested > 0 else "0%")
    kpi3.metric("Projected 2030 Value", f"₹{current_val * (1.12**4):,.0f}")

st.sidebar.info("v3.4 Stable Build | Ready for Public URL")
