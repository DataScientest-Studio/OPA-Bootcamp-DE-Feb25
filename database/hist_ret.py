import sys
import os
import psycopg2
import numpy as np
from datetime import datetime

# load host address
with open('host.txt', 'r') as file:
    lines = file.readlines()  # Returns a list of lines
    host_name = lines[0].strip()  # remove trailing white space
#connect database

# get the main dir
path = os.path.dirname(os.path.dirname(os.path.abspath("hist.py")))
# add retrival function folder to system path
sys.path.append(path + "/retrieval")
# import retrieval class
from crypto_retrieval import retrieval

# initialize class
ret = retrieval()

# retrieva data
data = ret.retrieve_hist(period_start="2025-01-17 00:00:00", interval_id="30m")

# make elements numeric
data = [[float(item) for item in sublist] for sublist in data]

# transfrom data into numpy array so that it is more workable - use object array for mixed data
data = np.array(data, dtype=object)

# transform open and close time to standard datetime format
data[:,0] = ret.unix_to_datetime(data[:,0])
data[:,6] = ret.unix_to_datetime(data[:,6])

# drop the last column, does not contain important info
data = np.delete(data, -1, 1)
print(data[0,])

""" write data into tables"""

#connect database
conn = psycopg2.connect(database="crypto_db",
                        host=host_name,
                        user="daniel",
                        password="datascientest",
                        port=5432)

# next create a cursor
cur = conn.cursor()

# record retrieval date
cur.execute("""
INSERT INTO Update_Record (Update_date)
VALUES (%s);""", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

# insert the primary keys coin
cur.execute("""
INSERT INTO Crypto_ID (Crypto_name)
SELECT %s
WHERE NOT EXISTS (
    SELECT 1 FROM Crypto_ID 
    WHERE Crypto_name = %s
);""", (ret.coin, ret.coin))

# insert the primary keys interval
cur.execute("""INSERT INTO Interval_ID (Interval_name)
SELECT %s
WHERE NOT EXISTS (
    SELECT 1 FROM Interval_ID 
    WHERE Interval_name = %s
);""", (ret.interval, ret.interval))

#commit changes
conn.commit()

 # same for interval
cur.execute("""SELECT Interval_ID
                FROM Interval_ID
                WHERE Interval_name = %s""", [ret.interval])
        
# get id
interval_id = cur.fetchone()

# same for crypto
cur.execute("""SELECT Crypto_ID
                FROM Crypto_ID
                WHERE Crypto_name = %s""", [ret.coin])

# get id
Coin_id = cur.fetchone()



# create array with currency name
np_cur = np.concatenate((
    np.tile(Coin_id, (data.shape[0], 1)),  # Create a column of 1s
    np.tile(interval_id, (data.shape[0], 1)),  # Create a column of 2s
    np.tile(ret.currency, (data.shape[0], 1))   # Create a column of 3s
), axis=1)  # Concatenate along columns

# concatenate with the data array
full_df = np.concatenate((np_cur, data), axis = 1)

# transform data back 
from io import StringIO

csv_data = StringIO()
np.savetxt(csv_data, full_df, delimiter='|', fmt='%s')  # Change delimiter to pipe
csv_data.seek(0)

cur.copy_from(
    csv_data,
    'main_tb',
    sep='|',  # Match the delimiter you used above
    columns=('crypto_id', 'interval_id', 'currency_name', 'open_time',
             'open_price', 'close_price', 'high_price', 'low_price',
             'volume', 'close_time',  'quote_asset_volume', 'nr_trades',
             'tb_based_asset_volume', 'tb_quote_asset_volume'))
# Commit the transaction
conn.commit()

# Close the connection
cur.close()
conn.close()
