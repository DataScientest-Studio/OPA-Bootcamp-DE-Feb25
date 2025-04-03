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
ret = retrieval(coin_list = ["XRP", "DOGE", "ETH"], interval_list = [ "1h", "1d"])

# save time at which we retriev data
update_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# retrieva data
#data = ret.retrieve_hist(period_start="2025-01-17 00:00:00", interval_id="30m")

# update historical tables 
ret.hist_update(period_start="2025-03-17 00:00:00",time_stamp=update_stamp, host_info=host_name)
