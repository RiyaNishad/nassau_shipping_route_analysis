# Nassau Candy Route Intelligence

A Streamlit dashboard for analyzing sales, route efficiency, delivery lead times, and product performance for Nassau Candy distribution data.

## Overview

This dashboard provides a clear operational view of:
- Sales and profit performance.
- State-wise route lead-time patterns.
- Product and division performance.
- Shipping mode and region filters.
- Detailed transaction-level audit data.

It is designed to help users quickly identify delays, high-performing products, and regional trends.

## Features

- Interactive customer order lookup.
- KPI cards for sales, profit, margin, late orders, average lead time, and status.
- Route lead-time choropleth map with state labels.
- Revenue and profit trend charts.
- Region-wise and product-wise analysis.
- Transaction ledger table.
- Customizable coffee-brown theme.

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly

## Files

- `app.py` — Main Streamlit application.
- `Nassau-Candy-Distributor.csv` — Dataset used by the dashboard.
- `README.md` — Project documentation.

## Dataset

The dataset includes fields such as:
- Order ID
- Order Date
- Ship Date
- Ship Mode
- Customer ID
- Region
- State/Province
- Product Name
- Sales
- Units
- Gross Profit
- Cost

## Setup Instructions

### 1. Clone or download the project
Place the following files in the same folder:
- `app.py`
- `Nassau-Candy-Distributor.csv`

### 2. Install dependencies

```bash
pip install streamlit pandas numpy plotly
```

### 3. Run the app

```bash
streamlit run app.py
```

## App Logic

- Enter a Customer Order ID to filter the dashboard.
- Use sidebar controls to filter by:
  - Region
  - Ship Mode
  - Product
  - Lead time range
- Explore insights across strategy, routes, products, and ledger tabs.

## Visual Theme

The dashboard uses a warm coffee-brown theme with:
- Dark cocoa background.
- Brown sidebar.
- Light cream text.
- Beige and caramel accents.

## Notes

- The app auto-detects the CSV file from the app folder, parent folder, or current working directory.
- If no data matches the selected filters, the app shows a warning message.

## License

Add your preferred license here.

## Author

Created for supply chain and sales intelligence analysis.
