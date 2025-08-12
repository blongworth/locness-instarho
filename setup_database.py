#!/usr/bin/env python3
"""
Script to create a sample SQLite database with streaming data.
This simulates sensor data being continuously added to a database.
"""

import sqlite3
import random
import time
from datetime import datetime, timedelta
import threading
import signal
import sys

def create_database():
    """Create the SQLite database and table."""
    conn = sqlite3.connect('streaming_data.db')
    cursor = conn.cursor()
    
    # Create table for sensor data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            pressure REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

def insert_sample_data():
    """Insert some initial sample data."""
    conn = sqlite3.connect('streaming_data.db')
    cursor = conn.cursor()
    
    # Insert some historical data (last 24 hours)
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(100):
        timestamp = base_time + timedelta(minutes=i * 14.4)  # Every ~14 minutes
        temperature = 20 + random.normalvariate(0, 5)  # Around 20°C with variation
        humidity = 50 + random.normalvariate(0, 10)    # Around 50% with variation
        pressure = 1013 + random.normalvariate(0, 20)  # Around 1013 hPa with variation
        
        cursor.execute('''
            INSERT INTO sensor_data (timestamp, temperature, humidity, pressure)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, temperature, humidity, pressure))
    
    conn.commit()
    conn.close()
    print("Sample data inserted successfully!")

def simulate_streaming_data():
    """Continuously insert new data to simulate streaming."""
    print("Starting streaming data simulation... Press Ctrl+C to stop.")
    
    def signal_handler(sig, frame):
        print("\nStopping streaming data simulation...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        try:
            conn = sqlite3.connect('streaming_data.db')
            cursor = conn.cursor()
            
            # Generate new data point
            temperature = 20 + random.normalvariate(0, 5)
            humidity = 50 + random.normalvariate(0, 10)
            pressure = 1013 + random.normalvariate(0, 20)
            
            cursor.execute('''
                INSERT INTO sensor_data (temperature, humidity, pressure)
                VALUES (?, ?, ?)
            ''', (temperature, humidity, pressure))
            
            conn.commit()
            conn.close()
            
            print(f"Inserted: T={temperature:.2f}°C, H={humidity:.2f}%, P={pressure:.2f}hPa")
            time.sleep(5)  # Insert new data every 5 seconds
            
        except Exception as e:
            print(f"Error inserting data: {e}")
            time.sleep(5)

if __name__ == "__main__":
    create_database()
    insert_sample_data()
    
    # Ask user if they want to start streaming simulation
    choice = input("Do you want to start streaming data simulation? (y/n): ").lower()
    if choice == 'y':
        simulate_streaming_data()
    else:
        print("Database setup complete. You can now run the Streamlit app.")
