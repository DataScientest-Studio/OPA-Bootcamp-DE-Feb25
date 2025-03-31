from crypto_retrieval import retrieval
from datetime import datetime
import pandas as pd

ret = retrieval()
data = ret.retrieve_hist(period_start="2025-01-17 00:00:00", interval_id="30m")

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
df = pd.DataFrame(columns=columns)

# append rows
# Create DataFrame
for i in range(len(data)):
    df.loc[i,] = data[i]

df['open_time'] = df['open_time'].apply(ret.unix_to_datetime)



