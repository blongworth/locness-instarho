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
        conn = sqlite3.connect('C:/Users/CSL 2/Documents/LOCNESS_data/database/locness.db')
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
        # Query to get recent data (assuming timestamp is stored as Unix integer seconds)
        query = f"""
        SELECT rho_ppb, datetime_utc AS timestamp
        FROM rhodamine
        WHERE timestamp >= strftime('%s', 'now', '-{hours_back} hours')
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            # Convert Unix integer seconds to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
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
        SELECT rho_ppb, datetime_utc AS timestamp
        FROM rhodamine
        ORDER BY timestamp DESC
        LIMIT 1
        """
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        if result:
            # Convert Unix integer seconds to readable datetime
            readable_time = datetime.fromtimestamp(result[1]).strftime('%Y-%m-%d %H:%M:%S')
            return {
                'rho_ppb': result[0],
                'timestamp': readable_time
            }
        return None
    except Exception as e:
        st.error(f"Error getting latest values: {e}")
        conn.close()
        return None

def create_time_series_chart(df):
    """Create a time series chart for rho_ppb vs timestamp."""
    if df.empty:
        return None
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['rho_ppb'],
                   mode='lines+markers', name='rho_ppb',
                   line=dict(color='#4ecdc4', width=2),
                   marker=dict(size=4))
    )
    fig.update_layout(
        height=500,
        showlegend=True,
        title_text="rho_ppb vs Timestamp",
        title_x=0.5,
        xaxis_title="Time",
        yaxis_title="rho_ppb"
    )
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
    st.sidebar.markdown("**Table:** `rhodamine`")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data(hours_back, data_limit)
        latest_values = get_latest_values()
    
    if df.empty:
        st.warning("No data found in the database. Please run `setup_database.py` first to create sample data.")
        st.info("To create sample data, run: `python setup_database.py`")
        return
    
    # Only show the rho_ppb vs timestamp plot and a simple data table
    st.subheader("📊 rho_ppb vs Timestamp")
    time_series_fig = create_time_series_chart(df)
    if time_series_fig:
        st.plotly_chart(time_series_fig, use_container_width=True)
    with st.expander("📋 Raw Data (Latest 20 records)"):
        st.dataframe(df.tail(20).iloc[::-1], use_container_width=True)
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
