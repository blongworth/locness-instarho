# Streaming Data Dashboard

A Streamlit application that visualizes streaming data from a SQLite database in real-time.

## Features

- 📊 Real-time time series charts for temperature, humidity, and pressure
- 🎯 Live gauge charts showing current sensor readings
- 📈 Automatic data refresh with configurable intervals
- 📋 Raw data table view
- 📈 Statistical summaries
- 🎛️ Interactive controls for time range and refresh settings

## Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Create the SQLite database with sample data:
   ```bash
   python setup_database.py
   ```
   
   This will:
   - Create a SQLite database (`streaming_data.db`)
   - Add sample historical data (last 24 hours)
   - Optionally start a background process to simulate streaming data

3. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

4. Open your browser to the URL shown in the terminal (usually `http://localhost:8501`)

## Database Schema

The app expects a SQLite table named `sensor_data` with the following structure:

```sql
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL,
    pressure REAL
);
```

## Usage

### Dashboard Controls

- **Auto-refresh**: Toggle automatic data refresh
- **Time range**: Select how much historical data to display (1-48 hours)
- **Max data points**: Limit the number of data points to prevent performance issues
- **Refresh interval**: Set how often the dashboard updates (1-30 seconds)

### Views

1. **Current Values**: Displays the latest sensor readings with trend indicators
2. **Time Series Charts**: Line charts showing data trends over time
3. **Gauge Charts**: Real-time gauges for current readings with thresholds
4. **Raw Data Table**: Expandable table showing the latest 20 records
5. **Statistics**: Mean, min, max, and standard deviation for each metric

### Simulating Streaming Data

To simulate continuous data streaming, run the database setup script and choose to start the streaming simulation:

```bash
python setup_database.py
# Choose 'y' when prompted to start streaming simulation
```

This will add new data points every 5 seconds. Keep this running in a separate terminal while using the Streamlit app to see real-time updates.

## Customization

You can easily modify the app to work with your own data:

1. Update the database connection in `streamlit_app.py`
2. Modify the SQL queries to match your table schema
3. Adjust the chart types and visualizations as needed
4. Add new metrics or sensors by updating the data loading functions

## Files

- `streamlit_app.py`: Main Streamlit application
- `setup_database.py`: Database creation and data simulation script
- `pyproject.toml`: Python project configuration with dependencies
- `streaming_data.db`: SQLite database (created when you run setup)