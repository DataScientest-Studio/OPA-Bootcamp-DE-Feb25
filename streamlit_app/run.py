import streamlit as st
from streamlit_extras.stateful_button import button
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import datetime as dt
from logging_OPA import logger

import time

# Define a stop event
#stop_event = threading.Event()

def main():
    logger.info("Create main GUI - START")

    #stop_event.clear()
    #thread = threading.Thread(target=run_websocket)
    #thread.start()

    st.title("Datascientest OPA project")

    supported_assets = ["MSFT", "BTC", "PEPE", "XRP"]
    asset = st.sidebar.selectbox("Select an asset...", options=supported_assets, index=0)

    end_date = dt.datetime.now()
    start_date = dt.datetime(end_date.year - 1, end_date.month, end_date.day)

    start_date = st.sidebar.date_input("Start date", value=start_date)
    end_date = st.sidebar.date_input("End date", value=end_date)

    data = yf.download(asset, start=start_date, end=end_date, auto_adjust=False)
    data_xs = data.xs(asset, axis=1,level='Ticker')
    if yf.__version__ != "0.2.59":
        st.error(f"YFinance version [{yf.__version__}] not supported. ")
    else:
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
#            st.markdown('<div class="centered-radio">', unsafe_allow_html=True)
            choice = st.radio(
                        label="",
                        options=("1d", "5d", "10d", "1m", "3m", "6m", "1y", "Max"),
                        index = 7,
                        horizontal = True
                    )
#            st.markdown('</div>', unsafe_allow_html=True)

        if choice == "1d":
            #1day data
            ...
        elif choice == "5d":
            #5days data
            ...
        elif choice == "Max":
            data_chart = data_xs

        fig = px.line(data_chart, x = data_chart.index, 
                    y = "Close", 
                    title = asset, 
                    labels = {"x":"Date", "y":"Price"})

        st.plotly_chart(fig, key="main_chart")

        pricing_data, tab2_data, tab3_data = st.tabs(["Pricing Data", "Tab 2", "Tab 3"])

        with pricing_data:
            st.header("Price changes")
            st.write(data_xs)
        
        with tab2_data:
            st.write("To be done")
            st.plotly_chart(fig, key="sub_chart")
        
        with tab3_data:
            st.write("To be done")

    #    st.on_session_end(cleanup)

    logger.info("Create main GUI - END")

# Clean up when Streamlit stops
def cleanup():
#    stop_event.set()
    time.sleep(1)  # Allow the thread to close gracefully


if __name__ == "__main__":
    main()