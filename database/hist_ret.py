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

