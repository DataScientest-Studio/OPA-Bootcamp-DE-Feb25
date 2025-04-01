import sys
import os
import psycopg2

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

""" write data into tables"""

#connect database
conn = psycopg2.connect(database="crypto_db",
                        host=host_name,
                        user="daniel",
                        password="datascientest",
                        port=5432)

# next create a cursor
cur = conn.cursor()



# insert the primary keys currency
cur.execute("""
INSERT INTO Currency_ID (Currency_name)
SELECT %s
WHERE NOT EXISTS (
    SELECT 1 FROM Currency_ID 
    WHERE Currency_name = %s
);
""", (ret.currency, ret.currency))

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

for row in data:
    # first drop the last index, that is garbage and the first which goes in another table:
    dat = row[1:-1]

    # transform time ID to standard datetime format
    time = ret.unix_to_datetime(row[0])


    # insert the primary key time
    cur.execute("""INSERT INTO Time_ID (Time_stamp)
    SELECT %s
    WHERE NOT EXISTS (
        SELECT 1 FROM Time_ID
        WHERE Time_stamp = %s
    );""", (time, time))

    #commit changes
    conn.commit()

    # next setup the list we will put in the main table by retrieving the relevant variables
    cur.execute("""SELECT Time_ID 
                FROM Time_ID
                WHERE Time_stamp = %s);""", time)
    
    # get id
    time_id = cur.fetchone()

    # same for interval
    cur.execute("""SELECT Interval_ID 
                FROM Interval_ID
                WHERE Interval_name = %s);""", ret.interval)
    
    # get id
    interval_id = cur.fetchone()

    # same for crypto
    cur.execute("""SELECT Crypto_ID 
                FROM Crypto_ID
                WHERE Crypto_name = %s);""", ret.coin)
    
    # get id
    Crypto_id = cur.fetchone()

    # same for currency
    cur.execute("""SELECT Currency_ID 
                FROM Currency_ID
                WHERE Currency_name = %s);""", ret.currency)
    
    # get id
    Currency_id = cur.fetchone()

    # put the full row together
    new_list = [time_id, Crypto_id , Currency_id, interval_id] + dat

    # insert in to the main database
    cur.execute("""INSERT INTO Main_Tb (Time_ID, Crypto_ID, Currency_ID, 
                Interval_ID, Open_price, Close_price, High_price, Low_price,
                Volume, Close_time, Nr_trades, Quote_asset_volume, TB_based_asset_volume,
                TB_quote_asset_volume)
                VALUES (%s);
                """, new_list)
    
    #commit changes
    conn.commit()