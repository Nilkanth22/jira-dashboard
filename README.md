# Jira Dashboard

A web-based dashboard for visualizing and managing Jira tickets.

## Quick Start

### Option 1: One-Click Startup (Recommended)
Simply **double-click** `start_dashboard.bat` - it will:
1. ✅ Update data from `data.csv`
2. ✅ Open the dashboard in your browser
3. ✅ Start the local server

### Option 2: Manual Steps
If you prefer to run commands manually:
```bash
# Step 1: Update data
python update_data.py

# Step 2: Start server
python -m http.server 8000
```

Then open: http://localhost:8000/dashboard.html

## Updating Data

1. Replace `data.csv` with your new CSV file
2. Double-click `start_dashboard.bat` (or run `python update_data.py`)
3. Refresh your browser

## Files

- `dashboard.html` - Main dashboard interface
- `update_data.py` - Script to process CSV and generate JSON files
- `data.csv` - Source data file
- `cases.json` - Generated case data
- `data.json` - Generated summary statistics
- `start_dashboard.bat` - One-click startup script

## Requirements

- Python 3.x
- pandas (`pip install pandas`)
