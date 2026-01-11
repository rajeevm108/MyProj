# MyProj
# Bullion Tracker & Valuer, Tax Calculator
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import io

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Bullion Pro 2026", layout="wide", page_icon="🏦")

# Custom CSS for a professional "Fintech Dark" look
st.markdown("""
    <style>
    .stMetric { background-color: #1e2129; border: 1px solid #3e4452; padding: 15px; border-radius: 10px; }
    [data-testid="stSidebar"] { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1e2129; border-radius: 5px; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL CONSTANTS (JAN 2026) ---
LIVE_GOLD = 140000 
LIVE_SILVER = 253000
LTCG_RATE = 0.125
STCG_SLAB = 0.20 # Standard 20% slab for calculation

# Initialize session state for persistent inventory
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=[
        "Metal", "Form", "Weight", "Buy Price", "Purchase Date"
    ])

# --- 3. LOGIC ENGINE ---
def calculate_audit(df):
    if df.empty: return None
    
    results = []
    today = date(2026, 1, 11)
    
    for _, row in df.iterrows():
        days = (today - row["Purchase Date"]).days
        # Indian Tax Rules: Physical (24m/730d) | Digital (12m/365d)
        threshold = 730 if row["Form"] == "Physical" else 365
        is_ltcg = days >= threshold
        
        market_p = LIVE_GOLD if row["Metal"] == "Gold" else LIVE_SILVER
        unit = 10 if row["Metal"] == "Gold" else 1000
        
        current_val = (row["Weight"] / unit) * market_p
        cost_basis = (row["Weight"] / unit) * row["Buy Price"]
        gain = current_val - cost_basis
        tax = (gain * LTCG_RATE) if is_ltcg else (gain * STCG_SLAB)
        
        results.append({
            "Asset": f"{row['Metal']} ({row['Form']})",
            "Weight (g)": row["Weight"],
            "Days Held": days,
            "Tax Bracket": "LTCG" if is_ltcg else "STCG",
            "Invested": round(cost_basis, 2),
            "Current Value": round(current_val, 2),
            "Unrealized Gain": round(gain, 2),
            "Tax Liability": round(max(0, tax), 2),
            "Post-Tax Value": round(current_val - max(0, tax), 2)
        })
    return pd.DataFrame(results)

# --- 4. NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Market Overview", "💼 Portfolio Manager", "📜 Tax Audit Report"])

with tab1:
    st.header("Real-Time Market Benchmarks")
    c1, c2, c3 = st.columns(3)
    c1.metric("Gold (10g)", f"₹{LIVE_GOLD:,.0f}", "+14.2% YoY")
    c2.metric("Silver (1kg)", f"₹{LIVE_SILVER:,.0f}", "+8.1% YoY")
    c3.metric("USD/INR", "₹92.45", "Strong")
    
    # Trend Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[2022, 2023, 2024, 2025, 2026], y=[52000, 61000, 82000, 115000, 140000],
                             name="Gold", line=dict(color="#FFD700", width=4)))
    fig.update_layout(template="plotly_dark", title="Gold Price Trajectory (2022-2026)", height=400)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Portfolio Entry")
    with st.expander("➕ Add New Bullion Holding", expanded=True):
        with st.form("entry_form"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                met = st.selectbox("Metal", ["Gold", "Silver"])
                form = st.radio("Form", ["Physical", "Digital"])
            with col_b:
                wgt = st.number_input("Weight in Grams", min_value=0.1, value=10.0)
                bp = st.number_input("Buy Price", min_value=1.0, value=75000.0)
            with col_c:
                dt = st.date_input("Purchase Date", value=date(2024, 1, 1))
                add = st.form_submit_button("Secure into Portfolio")
                
            if add:
                new_row = pd.DataFrame([[met, form, wgt, bp, dt]], columns=st.session_state.portfolio.columns)
                st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_row], ignore_index=True)
                st.toast("Holding added successfully!", icon="✅")

    if not st.session_state.portfolio.empty:
        st.subheader("Your Current Holdings")
        st.dataframe(st.session_state.portfolio, use_container_width=True)
        if st.button("🗑️ Reset Portfolio"):
            st.session_state.portfolio = st.session_state.portfolio.iloc[0:0]
            st.rerun()

with tab3:
    st.header("Compliance & Tax Auditor")
    audit_df = calculate_audit(st.session_state.portfolio)
    
    if audit_df is not None:
        # Dashboard Summary
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Asset Value", f"₹{audit_df['Current Value'].sum():,.0f}")
        m2.metric("Total Taxable Gain", f"₹{audit_df['Unrealized Gain'].sum():,.0f}")
        m3.metric("Total Est. Tax", f"₹{audit_df['Tax Liability'].sum():,.0f}", delta_color="inverse")
        
        st.markdown("---")
        st.dataframe(audit_df, use_container_width=True)
        
        # CSV Export logic
        csv = audit_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Official Audit Report (.csv)", data=csv, 
                           file_name=f"Tax_Report_{date.today()}.csv", mime="text/csv")
    else:
        st.warning("No data found. Please add holdings in the Portfolio Manager tab.")

# Sidebar Info
st.sidebar.image("https://img.icons8.com/color/96/gold-bars.png")
st.sidebar.title("Bullion Pro v4.0")
st.sidebar.info("Industry Standard Tool for Bullion Tax Management (FY 2025-26).")
