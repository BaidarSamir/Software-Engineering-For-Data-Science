import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime, timedelta

# Streamlit app title
st.title("📊 Bitcoin Price Analysis and Prediction Dashboard")

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

    # Tabbed interface
    tab1, tab2, tab3 = st.tabs(["Exploratory Data Analysis", "Visualization", "Prediction Model"])

    # Tab 1: EDA
    with tab1:
        st.subheader("Exploratory Data Analysis")
        st.dataframe(data)
        st.write(data.describe())

    # Tab 2: Visualization
    with tab2:
        st.subheader("Visualization Techniques")
        if "Close" in data.columns:
            # Interactive Line Chart with Plotly
            fig = px.line(data, x="Date", y=data["Close"].squeeze(), title="Bitcoin Closing Price Trend")
            st.plotly_chart(fig)

            # Correlation Heatmap
            correlation_matrix = data.corr()
            fig_corr = px.imshow(correlation_matrix, text_auto=True, title="Correlation Heatmap")
            st.plotly_chart(fig_corr)
        else:
            st.warning("Closing price data is unavailable for visualization.")

    # Tab 3: Prediction Model
    with tab3:
        st.subheader("Bitcoin Price Prediction")

        if "Close" in data.columns:
            # Prepare data for ML model
            data['Date'] = pd.to_datetime(data['Date'])
            data['Timestamp'] = data['Date'].map(datetime.timestamp)

            # Feature selection
            X = data[['Timestamp']]
            y = data['Close']

            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Model training
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Predictions
            y_pred = model.predict(X_test)

            # Model evaluation
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            st.write(f"Mean Squared Error: {mse:.2f}")
            st.write(f"R-squared: {r2:.2f}")

            # Future predictions
            st.write("### Future Price Prediction")
            future_days = st.slider("Days into the future", 1, 30, 7)
            future_timestamps = [(datetime.now() + timedelta(days=i)).timestamp() for i in range(future_days)]
            future_predictions = model.predict(pd.DataFrame(future_timestamps, columns=['Timestamp']))

            future_data = pd.DataFrame({
                "Date": [datetime.fromtimestamp(ts) for ts in future_timestamps],
                "Predicted Price": future_predictions.squeeze()
            })

            st.dataframe(future_data)

            # Plot future predictions
            fig_future = px.line(future_data, x="Date", y="Predicted Price", title="Future Bitcoin Price Prediction")
            st.plotly_chart(fig_future)
        else:
            st.warning("Insufficient data for building the prediction model.")
