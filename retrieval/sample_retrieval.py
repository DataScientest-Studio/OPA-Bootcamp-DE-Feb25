from crypto_retrieval import retrieval
from datetime import datetime
import pandas as pd
import numpy as np

ret = retrieval()
data = ret.retrieve_hist(period_start="2025-01-17 00:00:00", interval_id="30m")

# make elements numeric
data = [[float(item) for item in sublist] for sublist in data]

# transfrom data into numpy array so that it is more workable
data = np.array(data, dtype=object)

data[:,0] = ret.unix_to_datetime(data[:,0])

# Column names
columns = [
    'open_time', 
    'open', 
    'high', 
    'low', 
    'close', 
    'volume', 
    'close_time', 
    'quote_asset_volume', 
    'number_of_trades', 
    'taker_buy_base_asset_volume', 
    'taker_buy_quote_asset_volume', 
    'ignore'
]

print(data[0])
# Create DataFrame
#df = pd.DataFrame(columns=columns)

# append rows
# Create DataFrame
#for i in range(len(data)):
    #df.loc[i,] = data[i]

#df['open_time'] = df['open_time'].apply(ret.unix_to_datetime)



