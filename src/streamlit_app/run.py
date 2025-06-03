import streamlit as st
from streamlit_extras.stateful_button import button
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt

import sys
import logging
import time
import threading


#from logging_OPA import logger
from API.api_calls import api_get_coins, api_get_intervals, api_get_candels, api_get_available_models
import layout as app_ly

# Configure root logger to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Create main GUI - START")

    # get conttrol data 
    # supported coins and supported intervals
    try:
        coins = api_get_coins()
        if len(coins) == 0:
            logger.debug("No coins returned by the API.")
            st.error("No coins returned by the API.")
            #exit the application
            return
        intervals = api_get_intervals() 
        if len(intervals) == 0:
            logger.debug("No intervals returned by the API.")
            st.error("No intervals returned by the API.")
            #exit the application
            return
    except Exception as e:
        st.error(f"Error fetching data from API: {e}")
        #exit the application
        return

    supported_coins = list(coin["ticker"] for coin in coins)
    supported_intervals = list(interval["name_short"] for interval in intervals)
    
    st.set_page_config(layout="wide")

    app_ly.add_coin_images(st)

    st.markdown("""
        <div style='text-align: center; font-size: 2.75rem; font-weight: 800;'>
            DataScientest OPA project
        </div>
    """, unsafe_allow_html=True)


    st.sidebar.image("Images/DataScientest.jpg", use_container_width=True)

    asset = st.sidebar.selectbox("Select an asset...", options=supported_coins, index=0)

    end_date = dt.datetime.now()
    start_date = dt.datetime(end_date.year - 1, end_date.month, end_date.day)

    start_date = st.sidebar.date_input("Start date", value=start_date)
    end_date = st.sidebar.date_input("End date", value=end_date)

#    data = yf.download(asset, start=start_date, end=end_date, auto_adjust=False)
#    data_xs = data.xs(asset, axis=1,level='Ticker')

    st.markdown(
        """
        <style>
        .centered-radio {
            display: flex;
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    with st.container():
        st.markdown('<div class="centered-radio">', unsafe_allow_html=True)
        colInterval, _, _, colChartType = st.columns([1, 1, 1, 1])
        with colInterval:
            interval = st.radio(
                label="Interval: ",
                options=supported_intervals,
                index = 0, # select the first option by default
                horizontal = True
            )
        with colChartType:  
            chart_type = st.radio(
                label="Chart Type: ", 
                options=["Line", "Candlestick"],
                index=0,
                horizontal=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

    try:
        startDateParam = start_date.strftime("%Y%m%d000000")
        endDateParam = end_date.strftime("%Y%m%d000000")
        logger.info(f"Fetching candle data for asset: {asset}, start date: {startDateParam}, end date: {endDateParam}, interval: {interval}")
        data = api_get_candels(ticker=asset, startDate=startDateParam, endDate=endDateParam, interval=interval)
        if not data:
            logger.error(f"No data returned for the selected asset : {asset} and interval {interval}.")
            st.error("No data returned for the selected asset and interval.")
            return
        data_xs = pd.DataFrame(data)
        data_xs['Date'] = pd.to_datetime(data_xs['close_time'])
        data_xs.set_index('Date', inplace=True)
        data_xs = data_xs.sort_values('Date')

        # Compute average volume
        # avg_volume = data_xs['volume'].mean()

        # Compute normalized volume intensity (0–1 scale)
        data_xs['VolumeColorIntensity'] = (data_xs['volume'] - data_xs['volume'].min()) / (data_xs['volume'].max() - data_xs['volume'].min())

        # Determine the volume color based on the close and open prices
        data_xs['VolumeColor'] = data_xs.apply(app_ly.volume_color, axis=1)

    except Exception as e:
        st.error(f"Error fetching candle data: {e}")
        return

    if chart_type == "Line":
        fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.7, 0.3],
                subplot_titles=("", "Volume")
        )
        fig.add_trace(
            go.Scatter(
                x=data_xs.index,
                y=data_xs['close_price'],
                mode='lines+markers',
                name='Close',
                line=dict(color='blue', width=1.5)
            ), 
            row=1, 
            col=1
        )
        fig.add_trace(
            go.Bar(
                x=data_xs.index,
                y=data_xs['volume'],
                name='Volume',
                marker_color=data_xs['VolumeColor']  # Use the VolumeColor column for bar colors
            ),
            row=2, 
            col=1
        )
        fig.update_layout(xaxis_title='Date', yaxis_title='Price')
    else:
        fig = make_subplots(
            rows=2, 
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=("", "Volume")
        )
        fig.add_trace(
            go.Candlestick(
                x=data_xs.index,
                open=data_xs['open_price'],
                high=data_xs['high_price'],
                low=data_xs['low_price'],
                close=data_xs['close_price'],
                increasing_line_color='green',
                decreasing_line_color='red',
                name='Candlestick'
            ),
            row=1, 
            col=1
        )
        fig.add_trace(
            go.Bar(
                x=data_xs.index,
                y=data_xs['volume'],
                name='Volume',
                marker_color=data_xs['VolumeColor']  # Use the VolumeColor column for bar colors
            ),
            row=2, 
            col=1
        )
    # Update layout
    fig.update_layout(
        title='', 
        xaxis_title='Date', 
        yaxis_title='Price', 
        showlegend=False, 
        xaxis_rangeslider_visible=False
    )

    # Display chart
    st.plotly_chart(fig, key="main_chart")

    try:
        if "dataframe" in st.session_state:
            del st.session_state["dataframe"]
        models = api_get_available_models(asset)
        if models and len(models['models']) > 0:
            df = pd.DataFrame(api_get_available_models(asset)['models'])
            st.session_state["dataframe"] = df
    except Exception as e:
        logger.error(f"Error fetching available models: {e}")

    pricing_data_tab, ml_models_tab = st.tabs(["Pricing Data", "ML Models"])
    with ml_models_tab:
        if st.button("🧠 Train the model", key="train-btn"):
            st.info("This function is not yet activated")
        st.header(f"Available ML Models for ticker: {asset}")
        if "dataframe" in st.session_state:
            df = st.session_state["dataframe"]
            st.dataframe(df, use_container_width=True)

            # Use selectbox to choose a row by ID
            selected_name = st.selectbox("Select an item ID to delete:", df["name"])

            if st.button("🔮 Predict using selected model",key="predict-btn"):
                try:
                    # Update dataframe in session
                    st.session_state["dataframe"] = df[df["name"] != selected_name]
                    st.info("This function is not yet activated")
                except Exception as e:
                    st.error(f"Error deleting item {selected_id}: {e}")
        else:
            st.info("No ML models availble. Prediction function not available.")

    with pricing_data_tab:
        st.header("Price changes")
        st.dataframe(data_xs, use_container_width=True)
    
    logger.info("Create main GUI - END")

if __name__ == "__main__":
    main()