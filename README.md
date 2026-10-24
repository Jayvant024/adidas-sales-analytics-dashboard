# Adidas US Sales Analytics Dashboard

An interactive Streamlit dashboard for exploring Adidas US sales data.

## Features
- Filters for region, product, sales method, and invoice date
- KPI cards for revenue, operating profit, units sold, operating margin, and record count
- Revenue by region and sales method
- Revenue and operating profit by product category
- Monthly revenue trend
- Correlation heatmap
- Filtered data table and CSV download

## Run locally

1. Install Python 3.10 or later.
2. Extract this ZIP folder.
3. Open a terminal in the extracted `adidas_streamlit_dashboard` folder.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

6. Open the local URL Streamlit prints, usually https://adidas-sales-dashboard1.streamlit.app/.

The `adidas_cleaned.csv` file is included so the dashboard can run without uploading the original Excel file again.

## Dataset notes
The app expects the provided cleaned CSV and its columns. KPI totals are calculated from the filtered rows. Correlation describes association, not causation.
