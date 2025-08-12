#!/usr/bin/env python3
"""
Streamlit app for plotting streaming data from SQLite database.
This app displays real-time sensor data with auto-refreshing charts.
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Streaming Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_database_connection():
    """Get connection to SQLite database."""
    try:
        conn = sqlite3.connect('streaming_data.db')
        return conn
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None

def load_data(hours_back=24, limit=1000):
    """Load data from the database."""
    conn = get_database_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        # Query to get recent data
        query = """
        SELECT timestamp, temperature, humidity, pressure
        FROM sensor_data
        WHERE timestamp >= datetime('now', '-{} hours')
        ORDER BY timestamp DESC
        LIMIT {}
        """.format(hours_back, limit)
        
        df = pd.read_sql_query(query, conn)
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        conn.close()
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        conn.close()
        return pd.DataFrame()

def get_latest_values():
    """Get the most recent sensor values."""
    conn = get_database_connection()
    if conn is None:
        return None
    
    try:
        query = """
        SELECT temperature, humidity, pressure, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'temperature': result[0],
                'humidity': result[1],
                'pressure': result[2],
                'timestamp': result[3]
            }
        return None
        
    except Exception as e:
        st.error(f"Error getting latest values: {e}")
        conn.close()
        return None

def create_time_series_chart(df):
    """Create a time series chart with multiple metrics."""
    if df.empty:
        return None
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Temperature (°C)', 'Humidity (%)', 'Pressure (hPa)'),
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    # Temperature
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['temperature'],
                  mode='lines+markers', name='Temperature',
                  line=dict(color='#ff6b6b', width=2),
                  marker=dict(size=4)),
        row=1, col=1
    )
    
    # Humidity
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['humidity'],
                  mode='lines+markers', name='Humidity',
                  line=dict(color='#4ecdc4', width=2),
                  marker=dict(size=4)),
        row=2, col=1
    )
    
    # Pressure
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['pressure'],
                  mode='lines+markers', name='Pressure',
                  line=dict(color='#45b7d1', width=2),
                  marker=dict(size=4)),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Sensor Data Time Series",
        title_x=0.5
    )
    
    # Update x-axes
    fig.update_xaxes(title_text="Time", row=3, col=1)
    
    return fig

def create_gauge_charts(latest_values):
    """Create gauge charts for current values."""
    if not latest_values:
        return None, None, None
    
    # Temperature gauge
    temp_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=latest_values['temperature'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Temperature (°C)"},
        delta={'reference': 20},
        gauge={
            'axis': {'range': [None, 40]},
            'bar': {'color': "#ff6b6b"},
            'steps': [
                {'range': [0, 15], 'color': "lightblue"},
                {'range': [15, 25], 'color': "lightgreen"},
                {'range': [25, 40], 'color': "lightyellow"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 35
            }
        }
    ))
    temp_fig.update_layout(height=250)
    
    # Humidity gauge
    hum_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=latest_values['humidity'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Humidity (%)"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#4ecdc4"},
            'steps': [
                {'range': [0, 30], 'color': "lightcoral"},
                {'range': [30, 70], 'color': "lightgreen"},
                {'range': [70, 100], 'color': "lightblue"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    hum_fig.update_layout(height=250)
    
    # Pressure gauge
    press_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=latest_values['pressure'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Pressure (hPa)"},
        delta={'reference': 1013},
        gauge={
            'axis': {'range': [950, 1050]},
            'bar': {'color': "#45b7d1"},
            'steps': [
                {'range': [950, 990], 'color': "lightcoral"},
                {'range': [990, 1030], 'color': "lightgreen"},
                {'range': [1030, 1050], 'color': "lightyellow"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1040
            }
        }
    ))
    press_fig.update_layout(height=250)
    
    return temp_fig, hum_fig, press_fig

def main():
    """Main Streamlit app."""
    st.title("📊 Streaming Data Dashboard")
    st.markdown("Real-time sensor data visualization from SQLite database")
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    
    # Time range selection
    hours_back = st.sidebar.selectbox(
        "Time range (hours)",
        options=[1, 6, 12, 24, 48],
        index=3
    )
    
    # Data limit
    data_limit = st.sidebar.slider(
        "Max data points",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100
    )
    
    # Refresh interval
    if auto_refresh:
        refresh_interval = st.sidebar.slider(
            "Refresh interval (seconds)",
            min_value=1,
            max_value=30,
            value=5
        )
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Database info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Database:** `streaming_data.db`")
    st.sidebar.markdown("**Table:** `sensor_data`")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data(hours_back, data_limit)
        latest_values = get_latest_values()
    
    if df.empty:
        st.warning("No data found in the database. Please run `setup_database.py` first to create sample data.")
        st.info("To create sample data, run: `python setup_database.py`")
        return
    
    # Display current values
    if latest_values:
        st.subheader("📈 Current Values")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Temperature",
                f"{latest_values['temperature']:.1f}°C",
                delta=f"{latest_values['temperature'] - 20:.1f}"
            )
        
        with col2:
            st.metric(
                "Humidity",
                f"{latest_values['humidity']:.1f}%",
                delta=f"{latest_values['humidity'] - 50:.1f}"
            )
        
        with col3:
            st.metric(
                "Pressure",
                f"{latest_values['pressure']:.1f} hPa",
                delta=f"{latest_values['pressure'] - 1013:.1f}"
            )
        
        with col4:
            st.metric(
                "Last Update",
                latest_values['timestamp']
            )
    
    # Create and display charts
    st.subheader("📊 Time Series Data")
    
    # Time series chart
    time_series_fig = create_time_series_chart(df)
    if time_series_fig:
        st.plotly_chart(time_series_fig, use_container_width=True)
    
    # Gauge charts
    if latest_values:
        st.subheader("🎯 Current Readings")
        temp_gauge, hum_gauge, press_gauge = create_gauge_charts(latest_values)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(temp_gauge, use_container_width=True)
        with col2:
            st.plotly_chart(hum_gauge, use_container_width=True)
        with col3:
            st.plotly_chart(press_gauge, use_container_width=True)
    
    # Data table
    with st.expander("📋 Raw Data (Latest 20 records)"):
        st.dataframe(df.tail(20).iloc[::-1], use_container_width=True)
    
    # Statistics
    with st.expander("📈 Statistics"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Temperature")
            st.write(f"Mean: {df['temperature'].mean():.2f}°C")
            st.write(f"Min: {df['temperature'].min():.2f}°C")
            st.write(f"Max: {df['temperature'].max():.2f}°C")
            st.write(f"Std: {df['temperature'].std():.2f}°C")
        
        with col2:
            st.subheader("Humidity")
            st.write(f"Mean: {df['humidity'].mean():.2f}%")
            st.write(f"Min: {df['humidity'].min():.2f}%")
            st.write(f"Max: {df['humidity'].max():.2f}%")
            st.write(f"Std: {df['humidity'].std():.2f}%")
        
        with col3:
            st.subheader("Pressure")
            st.write(f"Mean: {df['pressure'].mean():.2f} hPa")
            st.write(f"Min: {df['pressure'].min():.2f} hPa")
            st.write(f"Max: {df['pressure'].max():.2f} hPa")
            st.write(f"Std: {df['pressure'].std():.2f} hPa")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
