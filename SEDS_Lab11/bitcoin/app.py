import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Streamlit app title with style
st.markdown(
    """<style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
    }
    </style>
    <div class="title">Bitcoin Price Analysis Dashboard</div>
    """, unsafe_allow_html=True
)

# Sidebar configuration
st.sidebar.header("Dynamic Data Loading")

# Date selection
def default_dates():
    today = datetime.today()
    start = today - timedelta(days=365)
    return start, today

start_date, end_date = default_dates()
start_date = st.sidebar.date_input("Start Date", start_date)
end_date = st.sidebar.date_input("End Date", end_date)

if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")

# Fetch Bitcoin data
@st.cache_data
def fetch_bitcoin_data(start, end):
    try:
        data = yf.download("BTC-USD", start=start, end=end)
        if not data.empty:
            data.reset_index(inplace=True)
            return data
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

data = fetch_bitcoin_data(start_date, end_date)

if data.empty:
    st.error("No data found for the selected range. Try adjusting the dates.")
else:
    st.success(f"Data loaded for {len(data)} days.")

    # Display raw data with style
    st.subheader("Raw Data")
    st.dataframe(data.style.set_properties(**{'background-color': '#f9f9f9',
                                              'color': '#000',
                                              'border-color': '#aaa'}))

    # Descriptive statistics with style
    st.subheader("Descriptive Statistics")
    st.write(data.describe().style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#4CAF50'),
                                           ('color', 'white'),
                                           ('font-weight', 'bold')]}]))

    # Interactive Visualizations
    st.subheader("Interactive Visualizations")

    # Price trend analysis
    st.write("### Price Trend Analysis")
    if "Close" in data.columns:
        st.line_chart(data.set_index("Date")["Close"], use_container_width=True)
    else:
        st.warning("Closing price data is unavailable.")

    # Advanced Statistical Visualization
    st.write("### Advanced Statistical Visualization")
    
    if "Close" in data.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data["Close"], bins=30, kde=True, color="#4CAF50", ax=ax)
        ax.set_title("Distribution of Closing Prices", fontsize=16, color="#4CAF50")
        ax.set_xlabel("Closing Price (USD)", fontsize=14)
        ax.set_ylabel("Frequency", fontsize=14)
        st.pyplot(fig)
    else:
        st.warning("Closing price data is unavailable for statistical visualization.")

    # Correlation heatmap
    st.write("### Correlation Heatmap")
    correlation_matrix = data.corr()

    if not correlation_matrix.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap", fontsize=16, color="#4CAF50")
        st.pyplot(fig)
    else:
        st.warning("Correlation heatmap cannot be generated due to insufficient data.")

    # Moving averages
    st.write("### Moving Averages")
    if "Close" in data.columns:
        short_window = st.sidebar.slider("Short-Term Moving Average Window", 5, 50, 20)
        long_window = st.sidebar.slider("Long-Term Moving Average Window", 50, 200, 100)

        data[f"SMA_{short_window}"] = data["Close"].rolling(window=short_window).mean()
        data[f"SMA_{long_window}"] = data["Close"].rolling(window=long_window).mean()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data["Date"], data["Close"], label="Closing Price", color="#000")
        ax.plot(data["Date"], data[f"SMA_{short_window}"], label=f"SMA {short_window}", color="#4CAF50")
        ax.plot(data["Date"], data[f"SMA_{long_window}"], label=f"SMA {long_window}", color="#FF5722")
        ax.set_title("Moving Averages", fontsize=16, color="#4CAF50")
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Price (USD)", fontsize=14)
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("Closing price data is unavailable for moving averages.")

    # Downloadable CSV
    st.sidebar.write("### Download Data")
    csv = data.to_csv().encode('utf-8')
    st.sidebar.download_button(label="Download CSV", data=csv, file_name="bitcoin_data.csv", mime="text/csv")
