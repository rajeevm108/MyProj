# MyProj
# Bullion Tracker & Valuer
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Bullion Tracker v3.0", layout="wide", page_icon="💰")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; border-radius: 10px; padding: 15px; border: 1px solid #3e4255; }
    div[data-testid="stMetricValue"] { color: #f1c40f; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data
def load_data():
    # Historical Data (1975-2026) - Expanded Dataset
    years = list(range(1975, 2027))
    gold_prices = [540, 630, 680, 720, 780, 1330, 1800, 1640, 1750, 2100, 2130, 2140, 2570, 3130, 3200, 3460, 3750, 4100, 4140, 4480, 4500, 4400, 4700, 4900, 5200, 5600, 6000, 6500, 7000, 7500, 8000, 8500, 9500, 10500, 12000, 14500, 18500, 26400, 31000, 29600, 28000, 26343, 27500, 29000, 31500, 35000, 38000, 48600, 52000, 56000, 60000, 75000, 141990]
    silver_prices = [1170, 1350, 1450, 1550, 1650, 2300, 2000, 1800, 1900, 2200, 3920, 3800, 4500, 5500, 6400, 6800, 7200, 7500, 7600, 7800, 7900, 7870, 8500, 9000, 9500, 10000, 10500, 11000, 12000, 13000, 14000, 15000, 17000, 19000, 22000, 25000, 27200, 49000, 59000, 48000, 40000, 36318, 40000, 45000, 50000, 55000, 60000, 63000, 70000, 80000, 89000, 95000, 248900]
    
    df = pd.DataFrame({"Year": years, "Gold": gold_prices, "Silver": silver_prices})
    return df

df = load_data()
LIVE_GOLD = 141990
LIVE_SILVER = 248900
LIVE_USD = 90.27

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("💎 Bullion Tracker v3.0")
menu = st.sidebar.selectbox("Go To", ["Market Analytics", "Portfolio Valuer", "Projections 2030"])

# --- 4. FEATURE A: MARKET ANALYTICS ---
if menu == "Market Analytics":
    st.header("📈 Historical Market Performance")
    
    # Selection Row
    col1, col2, col3 = st.columns(3)
    with col1:
        asset = st.selectbox("Select Asset", ["Gold", "Silver", "Both"])
    with col2:
        start, end = st.select_slider("Select Timeframe", options=df['Year'].tolist(), value=(1975, 2026))

    mask = (df['Year'] >= start) & (df['Year'] <= end)
    filtered_df = df[mask]

    # Plotly Interactivity
    fig = go.Figure()
    if asset in ["Gold", "Both"]:
        fig.add_trace(go.Scatter(x=filtered_df['Year'], y=filtered_df['Gold'], name="Gold (per 10g)", line=dict(color='#f1c40f', width=3)))
    if asset in ["Silver", "Both"]:
        fig.add_trace(go.Scatter(x=filtered_df['Year'], y=filtered_df['Silver'], name="Silver (per kg)", line=dict(color='#bdc3c7', width=3), yaxis="y2"))

    fig.update_layout(
        template="plotly_dark",
        title=f"{asset} Price Journey ({start}-{end})",
        xaxis_title="Year",
        yaxis=dict(title="Gold Price (INR)"),
        yaxis2=dict(title="Silver Price (INR)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 5. FEATURE B: PORTFOLIO VALUER ---
elif menu == "Portfolio Valuer":
    st.header("⚖️ Bullion Valuer & Gain Calculator")
    
    c1, c2 = st.columns(2)
    with c1:
        metal = st.radio("Asset Type", ["Gold", "Silver"])
        weight = st.number_input("Weight (Grams)", min_value=0.0, value=10.0)
    with c2:
        buy_price = st.number_input("Purchase Price (per 10g/kg)", min_value=0.0, value=60000.0)
        st.info(f"Today's Live Rate: ₹{LIVE_GOLD if metal=='Gold' else LIVE_SILVER:,.0f}")

    # Calculations
    current_rate = LIVE_GOLD if metal == "Gold" else LIVE_SILVER
    unit = 10 if metal == "Gold" else 1000
    
    current_val = (weight / unit) * current_rate
    invested_val = (weight / unit) * buy_price
    gain = current_val - invested_val
    gain_pct = (gain / invested_val) * 100 if invested_val > 0 else 0

    # Display Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Value (INR)", f"₹{current_val:,.0f}")
    m2.metric("Total Gain/Loss", f"₹{gain:,.0f}", f"{gain_pct:.2f}%")
    m3.metric("Value in USD", f"${current_val/LIVE_USD:,.2f}")

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Gemini AI • 2026 Edition")

