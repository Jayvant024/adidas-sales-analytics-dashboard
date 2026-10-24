import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Adidas Sales Analytics", page_icon="👟", layout="wide")

st.title("👟 Adidas US Sales Analytics Dashboard")
st.caption("Interactive sales, profitability, product, region, and sales-channel analysis")

@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "adidas_cleaned.csv"
    data = pd.read_csv(csv_path, parse_dates=["Invoice Date"])
    data = data.dropna(how="all")
    for col in ["Price per Unit", "Units Sold", "Total Sales", "Operating Profit", "Operating Margin"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    data["Invoice Date"] = pd.to_datetime(data["Invoice Date"], errors="coerce")
    return data

df = load_data()

required = ["Invoice Date", "Region", "Product", "Sales Method", "Total Sales",
            "Operating Profit", "Units Sold", "Operating Margin"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Required columns are missing from the dataset: {', '.join(missing)}")
    st.stop()

st.sidebar.header("Filter the data")
regions = sorted(df["Region"].dropna().unique().tolist())
products = sorted(df["Product"].dropna().unique().tolist())
methods = sorted(df["Sales Method"].dropna().unique().tolist())

selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_products = st.sidebar.multiselect("Product category", products, default=products)
selected_methods = st.sidebar.multiselect("Sales method", methods, default=methods)

valid_dates = df["Invoice Date"].dropna()
if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    selected_dates = st.sidebar.date_input(
        "Invoice date range", value=(min_date, max_date),
        min_value=min_date, max_value=max_date
    )
else:
    selected_dates = ()

filtered = df[
    df["Region"].isin(selected_regions)
    & df["Product"].isin(selected_products)
    & df["Sales Method"].isin(selected_methods)
].copy()

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered = filtered[
        filtered["Invoice Date"].dt.date.between(start_date, end_date)
    ]

if filtered.empty:
    st.warning("No records match these filters. Adjust the filters in the sidebar.")
    st.stop()

total_sales = filtered["Total Sales"].sum()
total_profit = filtered["Operating Profit"].sum()
total_units = filtered["Units Sold"].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales else 0
orders = len(filtered)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${total_sales:,.0f}")
k2.metric("Operating Profit", f"${total_profit:,.0f}")
k3.metric("Units Sold", f"{total_units:,.0f}")
k4.metric("Operating Margin", f"{profit_margin:.2f}%")
k5.metric("Sales Records", f"{orders:,}")

st.divider()

left, right = st.columns(2)
with left:
    region_sales = filtered.groupby("Region", as_index=False)["Total Sales"].sum().sort_values("Total Sales", ascending=False)
    fig = px.bar(region_sales, x="Region", y="Total Sales", title="Revenue by Region",
                 labels={"Total Sales": "Revenue (USD)"}, color="Region")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    method_sales = filtered.groupby("Sales Method", as_index=False)["Total Sales"].sum().sort_values("Total Sales", ascending=False)
    fig = px.bar(method_sales, x="Sales Method", y="Total Sales", title="Revenue by Sales Method",
                 labels={"Total Sales": "Revenue (USD)"}, color="Sales Method")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    product_sales = filtered.groupby("Product", as_index=False)["Total Sales"].sum().sort_values("Total Sales", ascending=True)
    fig = px.bar(product_sales, x="Total Sales", y="Product", orientation="h",
                 title="Revenue by Product Category", labels={"Total Sales": "Revenue (USD)"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    product_profit = filtered.groupby("Product", as_index=False)["Operating Profit"].sum().sort_values("Operating Profit", ascending=True)
    fig = px.bar(product_profit, x="Operating Profit", y="Product", orientation="h",
                 title="Operating Profit by Product", labels={"Operating Profit": "Profit (USD)"})
    st.plotly_chart(fig, use_container_width=True)

monthly = filtered.dropna(subset=["Invoice Date"]).set_index("Invoice Date")["Total Sales"].resample("MS").sum().reset_index()
monthly.columns = ["Month", "Total Sales"]
fig = px.line(monthly, x="Month", y="Total Sales", markers=True, title="Monthly Revenue Trend",
              labels={"Total Sales": "Revenue (USD)", "Month": "Month"})
st.plotly_chart(fig, use_container_width=True)

st.subheader("Correlation Heatmap")
numeric_cols = ["Price per Unit", "Units Sold", "Total Sales", "Operating Profit", "Operating Margin"]
corr = filtered[numeric_cols].corr(numeric_only=True)
fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1, title="Correlation Between Numeric Variables")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Key findings for the current filters")
top_region = region_sales.iloc[0]
top_product = product_sales.iloc[-1]
top_method = method_sales.iloc[0]
c1, c2, c3 = st.columns(3)
c1.info(f"**Top region by revenue:** {top_region['Region']} (${top_region['Total Sales']:,.0f})")
c2.info(f"**Top product by revenue:** {top_product['Product']} (${top_product['Total Sales']:,.0f})")
c3.info(f"**Top sales method:** {top_method['Sales Method']} (${top_method['Total Sales']:,.0f})")

st.subheader("Filtered data")
st.dataframe(filtered, use_container_width=True, hide_index=True)
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data as CSV", data=csv_bytes,
                   file_name="adidas_filtered_sales.csv", mime="text/csv")

st.caption("Dataset: Adidas US Sales. Revenue and profit values are shown in USD. Correlation indicates association, not causation.")
