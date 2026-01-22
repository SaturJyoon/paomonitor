import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Plant Monitoring System",
    page_icon="🌱",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        margin-bottom: 30px;
    }
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 10px;
    }
    .logo {
        font-size: 2.8rem;
    }
    .logo-text h1 {
        margin: 0;
        font-size: 2.2rem;
    }
    .logo-text p {
        margin: 0;
        opacity: 0.8;
    }
    .connection-status {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 10px 20px;
        border-radius: 25px;
        background-color: rgba(255, 255, 255, 0.1);
        margin-top: 15px;
    }
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #4CAF50;
    }
    .status-dot.disconnected {
        background-color: #ff5252;
    }
    .card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .plant-info {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    .plant-icon {
        font-size: 2rem;
    }
    .plant-details h4 {
        margin: 0;
        font-size: 1rem;
    }
    .plant-details p {
        margin: 0;
        color: #666;
        font-size: 0.9rem;
    }
    .control-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    footer {
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        color: #666;
        font-size: 0.9rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


if 'data_points' not in st.session_state:
    st.session_state.data_points = []
if 'humidity' not in st.session_state:
    st.session_state.humidity = 50
if 'temperature' not in st.session_state:
    st.session_state.temperature = 22
if 'moisture' not in st.session_state:
    st.session_state.moisture = 60
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'auto_generate' not in st.session_state:
    st.session_state.auto_generate = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = "Never"

def get_status(value, min_val, max_val):
    if min_val <= value <= max_val:
        return "Optimal"
    elif value < min_val:
        return "Too low"
    else:
        return "Too high"

def create_chart(time_filter=24):
    if not st.session_state.data_points:
        return go.Figure()
    
    df = pd.DataFrame(st.session_state.data_points)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter by time
    cutoff = datetime.now() - timedelta(hours=time_filter)
    df = df[df['timestamp'] >= cutoff]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['humidity'], mode='lines+markers', name='Humidity (%)'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], mode='lines+markers', name='Temperature (°C)'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['moisture'], mode='lines+markers', name='Soil Moisture (%)'))
    
    fig.update_layout(
        title="Plant Data Over Time",
        xaxis_title="Time",
        yaxis_title="Value",
        template="plotly_white"
    )
    return fig

# Header
st.markdown("""
<div class="main-header">
    <div class="logo-container">
        <div class="logo">🌱</div>
        <div class="logo-text">
            <h1>Plant Monitoring System</h1>
            <p>Samsung Innovation Campus Project</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.subheader("Current Readings")
col1, col2, col3 = st.columns(3)

with col1:
    status = get_status(st.session_state.humidity, 40, 60)
    st.metric("Air Humidity", f"{st.session_state.humidity}%", delta=status)
    st.markdown("""
    <div class="plant-info">
        <div class="plant-icon">💧</div>
        <div class="plant-details">
            <h4>Optimal Range: 40-60%</h4>
            <p>For most indoor plants</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    status = get_status(st.session_state.temperature, 18, 24)
    st.metric("Temperature", f"{st.session_state.temperature}°C", delta=status)
    st.markdown("""
    <div class="plant-info">
        <div class="plant-icon">🌡️</div>
        <div class="plant-details">
            <h4>Optimal Range: 18-24°C</h4>
            <p>For most indoor plants</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    status = get_status(st.session_state.moisture, 40, 80)
    st.metric("Soil Moisture", f"{st.session_state.moisture}%", delta=status)
    st.markdown("""
    <div class="plant-info">
        <div class="plant-icon">🌱</div>
        <div class="plant-details">
            <h4>Optimal Range: 40-80%</h4>
            <p>Varies by plant type</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Chart Section
st.subheader("Data Visualization")
time_options = {"1 Hour": 1, "6 Hours": 6, "24 Hours": 24, "1 Week": 168}
selected_time = st.selectbox("Select Time Range", list(time_options.keys()), index=2)
time_filter = time_options[selected_time]

fig = create_chart(time_filter)
st.plotly_chart(fig, use_container_width=True)

# Controls
st.subheader("Controls")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### MQTT Configuration")
    broker_url = st.text_input("Broker URL", "wss://test.mosquitto.org:8081")
    topic = st.text_input("Topic to Subscribe", "samsung-innovation-campus/plant-data")
    client_id = st.text_input("Client ID", "", placeholder="Leave empty for random ID")
    
    if st.button("🔌 Connect to MQTT"):
        st.session_state.connected = True
        st.success("Connected to MQTT broker (simulated)")
    
    if st.button("🔌 Disconnect"):
        st.session_state.connected = False
        st.info("Disconnected from MQTT broker")
    
    st.markdown('</div>', unsafe_allow_html=True)
