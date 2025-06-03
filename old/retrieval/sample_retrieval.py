from crypto_retrieval import retrieval
from datetime import datetime
import pandas as pd
import numpy as np
import time
import requests

from binance.spot import Spot

client = Spot()

def datetime_to_unix(dt_str, format_str='%Y-%m-%d %H:%M:%S'):
        """
        Convert a datetime string to Unix timestamp
        
        Parameters:
        dt_str (str): Datetime string to convert
        format_str (str): Format of the input datetime string
        
        Returns:
        int: Unix timestamp in seconds
        """
        if isinstance(dt_str, (int, float, complex)):
            return(dt_str)
        else:
            # Parse the datetime string to a datetime object
            dt_object = datetime.strptime(dt_str, format_str)
            
            # Convert to Unix timestamp (seconds since epoch)
            unix_time = int(dt_object.timestamp())
            
        return unix_time

coin ='BTC'
currency = 'USDT'
interval_id="1m"
period_start= datetime_to_unix("2025-03-17 00:00:00")
period_end= datetime_to_unix("2025-04-06 00:00:00")

period_start = datetime_to_unix(
  
#save important variables
currency =  currency
interval = interval_id



        
symbol = coin + currency

        
base_url = "https://api.binance.com/api/v4/klines"
  
params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": period_start,
            "endTime": period_end,
            "limit":    1000
        }

start_time = time.time()
response = requests.get(base_url, params=params)
stop_time = time.time()

print("The duration to call the API was :", stop_time - start_time)