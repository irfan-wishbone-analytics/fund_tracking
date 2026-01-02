import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Legis1 Portfolio Engine")

st.sidebar.title("Configuration")
portfolio_val = st.sidebar.number_input("Portfolio Size", value=100000)
risk_per_trade = st.sidebar.slider("Risk per Trade %", 0.5, 5.0, 2.0) / 100

st.title("📊 Options Strategy Dashboard")

# Example UI for Trade Analysis
st.subheader("Trade Drill-down")
# (Logic to select trade from log would go here)

# Visualization
def plot_performance(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['PnL_R'], name="R Value", line=dict(color='white')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Underlying'], name="Price", yaxis="y2", opacity=0.3))
    
    # Red/Green Shading
    for i in range(len(df)-1):
        color = "rgba(0, 255, 0, 0.1)" if df['PnL_R'].iloc[i] > 0 else "rgba(255, 0, 0, 0.1)"
        fig.add_vrect(x0=df['Date'].iloc[i], x1=df['Date'].iloc[i+1], fillcolor=color, layer="below", line_width=0)

    fig.update_layout(yaxis2=dict(overlaying='y', side='right'), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)