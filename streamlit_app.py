import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import threading

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    try:
        if rc == 0:
            st.session_state.mqtt_connected = True
            client.subscribe(st.session_state.get('sensor_topic', 'samsung-innovation-campus/plant-data'))
            client.subscribe(st.session_state.get('prediction_topic', 'samsung-innovation-campus/prediction'))
        else:
            st.session_state.mqtt_connected = False
    except:
        pass  # Session state might not be available in callback context

def on_disconnect(client, userdata, rc):
    try:
        st.session_state.mqtt_connected = False
    except:
        pass

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        
        if topic == st.session_state.get('sensor_topic', 'samsung-innovation-campus/plant-data'):
            # Parse sensor data and update charts
            try:
                data = eval(payload)  # Assuming JSON-like string
                if 'temperature' in data:
                    st.session_state.temperature = data['temperature']
                if 'humidity' in data:
                    st.session_state.humidity = data['humidity']
                if 'soil_moisture' in data:
                    st.session_state.soil_moisture = data['soil_moisture']
            except:
                pass
        elif topic == st.session_state.get('prediction_topic', 'samsung-innovation-campus/prediction'):
            st.session_state.prediction = payload
    except:
        pass

st.set_page_config(
    page_title="Plant Monitoring System",
    page_icon="🌱",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
    body {
        font-family: 'JetBrains Mono', monospace;
    }
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
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
        background-color: rgba(240, 244, 224, 0.8);
        margin-top: 15px;
    }
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #228B22;
    }
    .status-dot.disconnected {
        background-color: #ff5252;
    }
    .card {
        background: #F0F4E0;
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
        border-top: 1px solid #D4EDDA;
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
        color: #556B2F;
        font-size: 0.9rem;
    }
    .control-card {
        background: #F0F4E0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    footer {
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        color: #556B2F;
        font-size: 0.9rem;
        border-top: 1px solid #D4EDDA;
    }
    .prediction-box {
        background: rgba(85, 107, 47, 0.8);
        border-radius: 10px;
        padding: 10px 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        font-size: 1rem;
        color: white;
    }
    .buzzer-box {
        background: rgba(85, 107, 47, 0.8);
        border-radius: 10px;
        padding: 5px 15px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        font-size: 0.9rem;
        color: white;
        text-align: center;
    }
    .right-section {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .section-box {
        background: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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
if 'prediction' not in st.session_state:
    st.session_state.prediction = "No prediction available"
if 'buzzer' not in st.session_state:
    st.session_state.buzzer = "Off"
if 'mqtt_connected' not in st.session_state:
    st.session_state.mqtt_connected = False
if 'mqtt_client' not in st.session_state:
    st.session_state.mqtt_client = None
if 'sensor_topic' not in st.session_state:
    st.session_state.sensor_topic = "samsung-innovation-campus/plant-data"
if 'prediction_topic' not in st.session_state:
    st.session_state.prediction_topic = "samsung-innovation-campus/prediction"
if 'output_topic' not in st.session_state:
    st.session_state.output_topic = "samsung-innovation-campus/output"
if 'broker_url' not in st.session_state:
    st.session_state.broker_url = "test.mosquitto.org"

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
            <p>By: DI-Binary</p>
        </div>
    </div>
    <div class="right-section">
        <div class="prediction-box">
            Prediction: """ + st.session_state.prediction + """
        </div>
        <div class="buzzer-box">
            Buzzer: """ + st.session_state.buzzer + """
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-box">', unsafe_allow_html=True)
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
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("Data Visualization")
time_options = {"1 Hour": 1, "6 Hours": 6, "24 Hours": 24, "1 Week": 168}
selected_time = st.selectbox("Select Time Range", list(time_options.keys()), index=2)
time_filter = time_options[selected_time]

fig = create_chart(time_filter)
st.plotly_chart(fig, width='stretch')
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("Controls")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### MQTT Configuration")
    broker_url = st.text_input("Broker URL", st.session_state.broker_url)
    sensor_topic = st.text_input("Sensor Topic", st.session_state.sensor_topic)
    prediction_topic = st.text_input("Prediction Topic", st.session_state.prediction_topic)
    output_topic = st.text_input("Output Topic", st.session_state.output_topic)
    
    # Update session state with current inputs
    st.session_state.broker_url = broker_url
    st.session_state.sensor_topic = sensor_topic
    st.session_state.prediction_topic = prediction_topic
    st.session_state.output_topic = output_topic
    
    if st.button("🔌 Connect to MQTT"):
        if st.session_state.get('mqtt_connected', False):
            st.info("Already connected to MQTT broker")
        else:
            try:
                # Clean up any existing client
                if st.session_state.get('mqtt_client'):
                    try:
                        st.session_state.mqtt_client.disconnect()
                        st.session_state.mqtt_client.loop_stop()
                    except:
                        pass
                
                # Parse broker URL and create appropriate client
                if broker_url.startswith("wss://") or broker_url.startswith("ws://"):
                    client = mqtt.Client(transport="websockets")
                    if broker_url.startswith("wss://"):
                        host = broker_url.replace("wss://", "").split(":")[0]
                        port = 8081  # Default WebSocket port
                        if ":" in broker_url.replace("wss://", ""):
                            port_str = broker_url.replace("wss://", "").split(":")[1]
                            if port_str:
                                port = int(port_str)
                    else:  # ws://
                        host = broker_url.replace("ws://", "").split(":")[0]
                        port = 8080  # Default WebSocket port
                        if ":" in broker_url.replace("ws://", ""):
                            port_str = broker_url.replace("ws://", "").split(":")[1]
                            if port_str:
                                port = int(port_str)
                    client.ws_set_options(path="/mqtt")
                else:
                    client = mqtt.Client()
                    host = broker_url.split(":")[0] if ":" in broker_url else broker_url
                    port = int(broker_url.split(":")[1]) if ":" in broker_url else 1883
                
                client.on_connect = on_connect
                client.on_disconnect = on_disconnect
                client.on_message = on_message
                
                client.connect(host, port, 60)
                client.loop_start()
                st.session_state.mqtt_client = client
                st.success("Connecting to MQTT broker...")
            except Exception as e:
                st.error(f"Failed to connect to MQTT broker: {str(e)}")
                st.session_state.mqtt_connected = False
    
    if st.button("🔌 Disconnect"):
        if st.session_state.get('mqtt_client'):
            try:
                st.session_state.mqtt_client.disconnect()
                st.session_state.mqtt_client.loop_stop()
                st.session_state.mqtt_client = None
                st.session_state.mqtt_connected = False
                st.session_state.connected = False
                st.session_state.prediction = "No prediction available"
                st.session_state.buzzer = "Off"
                st.info("Disconnected from MQTT broker")
            except Exception as e:
                st.error(f"Error disconnecting: {str(e)}")
        else:
            st.info("Not connected to MQTT broker")
    
    # Display connection status
    if st.session_state.mqtt_connected:
        st.success("✅ Connected to MQTT broker")
    else:
        st.warning("❌ Not connected to MQTT broker")
    
    st.markdown('</div>', unsafe_allow_html=True)
