import requests
import json
from datetime import datetime
from time import sleep
from functools import wraps
import inspect
from math import floor
import pandas as pd
import numpy as np
from io import StringIO
import psycopg2
import logging

from .db_connection import get_connection, close_connection

logger = logging.getLogger(__name__) 

class retrieval_handler():
    def __init__(self, limit = 1000, coin_list = [], interval_list = [], end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        """
        Parameters:
        limit (int): Number of records to retrieve (max 1000)
        """
        self.limit = limit
        self.counter = 0
        # Apply the decorator to the method after initialization
        self.retrieve_hist = self.batch_decorator(self.retrieve_hist)
        self.interval_list = interval_list
        self.coin_list = coin_list
        self.period_end = end

    def batch_decorator(self, func):
    # Decorator that checks if batch size exceeds limit - if so calls retrieval multiple times
        @wraps(func)
        def wrapper(*args, **kwargs):

            # Extract parameters from kwargs or use defaults
            p_start = kwargs.get('period_start', [])
            p_end = kwargs.get('period_end', self.period_end)
            self.interval_id = kwargs.get('interval_id', "1d")
            
            # Set date attributes
            start = self.datetime_to_unix(p_start) * 1000
            end = self.datetime_to_unix(p_end) * 1000

            #save once for final comparison
            self.final = self.datetime_to_unix(p_end) * 1000
            
            # Initialize variables
            results = []
            # call batch_info safely
            batch_info = self.batch_steps(date_start = start, date_stop = end)
            
            print(batch_info)

            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Check if batching is not needed
            if batch_info["batch_size"] < self.limit:
                bound_args.arguments['period_start'] = start
                bound_args.arguments['period_end'] = end  
                return func(*bound_args.args, **bound_args.kwargs)
            
            # Calculate number of calls needed
            call_nr = floor(batch_info['batch_size']/self.limit)
            print(call_nr)
    
           
            
            # Loop to retrieve all batches
            for call in range(call_nr):
                print("A call made")
                bound_args.arguments['period_start'] = start
                end = start + batch_info['step_size'] * self.limit
                bound_args.arguments['period_end'] = end

                # Call the original function with modified arguments
                batch_result = func(*bound_args.args, **bound_args.kwargs)
                print(batch_result)
        
                if batch_result:  # Only append if there are results
                    results.append(batch_result)
                    
                # Update the new start point
                start = end 
    
            
            # Check if we need a final call for remaining data
            
            if start < self.final:
                print("Final stop reached")
                bound_args.arguments['period_start'] = start
                end = self.final
                bound_args.arguments['period_end'] = end

                batch_result = func(*bound_args.args, **bound_args.kwargs)
                if batch_result:
                    results.append(batch_result)
            # Combine results if needed
            if len(results) == 1:
                return results[0]
            elif isinstance(results[0], list):
                # Flatten if results are lists
                return [item for sublist in results for item in sublist]
            
        return wrapper  # Return the wrapper function
    

    # main functions
    def retrieve_hist(self, coin ='BTC', currency = 'USDT', interval_id="1d", period_start= [] , period_end=[]):
        """
        Retrieves data for specified coins at specific markets
        
        Parameters:
        interval_id (str):  Interval resolution in minutes hours or days, permitted strings are '1d', '4h', '1h', '15m'
        symbol (str): string indicating they currency name, default is 'BTCUSDT'
        period_start (str): Start datetime string e.g. "2019-03-12 12:30:45"
        period_end (str): End datetime string e.g "2025-03-12 12:30:45"
        
        Returns:
        API infos can be found at:
        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
        data: JSON file format data
        Format:

        [
            [
            1499040000000,      // Open time
            "0.01634790",       // Open
            "0.80000000",       // High
            "0.01575800",       // Low
            "0.01577100",       // Close
            "148976.11427815",  // Volume
            1499644799999,      // Close time
            "2434.19055334",    // Quote asset volume
            308,                // Number of trades
            "1756.87402397",    // Taker buy base asset volume
            "28.46694368",      // Taker buy quote asset volume
            "17928899.62484339" // Ignore.
            ]
        ]
        """
        #save important variables
        self.currency =  currency
        self.interval = interval_id
        self.coin = coin

        # put together currency and coin
        symbol = self.coin + self.currency

        #base_url = "http://api.coincap.io/v2/assets/bitcoin/history"
        base_url = "https://api.binance.com/api/v3/klines"

        # update counter to not exceed binance limits:
        self.limit_check()
        
        # Parameters - using a dictionary makes it cleaner
        params_str = f"symbol={symbol}&interval={self.interval}&startTime={period_start}&endTime={period_end}&limit={self.limit}"
        url_to_call = f"{base_url}?{params_str}"

        logger.info(f"Calling URL: {url_to_call}")
        response = requests.get(url_to_call)

        return(response.json())

    
    def stream(self, coin_id, market_id='binance') :
        
        """
        Streams live data for specified coins at specific markets
        
        Parameters:
        coin_id (str): string indicating they currency name
        market_id (str): string indicating they exchange name
        
        Returns:
        data: JSON file format data
        """
         

    ### Helper functions
    def datetime_to_unix(self, dt_str, format_str='%Y-%m-%d %H:%M:%S'):
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
    
    def unix_to_datetime(self, dt_str, format_str='%Y-%m-%d %H:%M:%S'):
        """
        Convert a datetime string to Unix timestamp
        
        Parameters:
        dt_str (str): Datetime string to convert
        format_str (str): Format of the input datetime string
        
        Returns:
        int: Unix timestamp in seconds
        """

        # vectorized processing if we have more than one value
        if len(dt_str) > 1:
            # Convert to numpy array and process all at once
            timestamps_array = dt_str / 1000

            # Using pandas to vectorize the conversion
            formatted_date = pd.to_datetime(timestamps_array, unit='s').strftime(format_str).tolist()
        else:  
            # Convert Unix timestamp to datetime object
            dt_object = datetime.fromtimestamp(int(dt_str)/1000)
        
            # Format datetime object as string
            formatted_date = dt_object.strftime(format_str)
                
        return formatted_date
    
    def request_fun(self, url_str, pl={}, hd={}):
        """
        Call coin cap API
        
        Parameters:
        url_str (str): url string to be requested
        pl (dict): Optional parameter to call for instance start and end date
        pl (dict): Optional parameter header file
        
        Returns:
        new_data (JSON): returns JSON data
        """

        payload = pl
        headers = hd
        response = requests.request("GET", url_str, headers=headers, data=payload)

        # Parse the JSON response
        new_data = json.loads(response.text)
        return(new_data)
    
    def get_symbol_names(self):
        """
        Retrieve names of available exchanges on coin cap
        
        Parameters:

        
        Returns:
        list: returns list of exhcange names
        """

        url = "https://api.binance.com/api/v3/exchangeInfo"
        data = self.request_fun(url_str=url)
        #ex_names = [ex_data['exchangeId'] for ex_data in data['data']]
        return(data)
    
    def batch_steps(self, date_start, date_stop):
        """
        # determine stepsize by unit because the limit for retrieval is 1000 on binance
        
        Parameters:
        self.interval_id (str) -  Interval resolution in hours, days or weeks, permitted strings are '1w', '1d', '1h'
        self.date_stop (int) - Start datetime string transformed to Unix time
        
        Returns:
        dict: returns dictionary with the total batch size and the step size
        """
        
        if self.interval_id[-1]== 'h':
            step_size = 60*60*1000*int(self.interval_id[:-1])
        elif self.interval_id[-1]== 'd':
            step_size = 24*60*60*1000*int(self.interval_id[:-1])
        elif self.interval_id[-1]== 'w':
            step_size = 7*24*60*60*1000*int(self.interval_id[:-1])
        else:
            logging.error(f"Invalid interval_id {self.interval_id}. Use '1w', '1d', or '1h'.")
            raise ValueError("Invalid interval_id. Use '1w', '1d', or '1h'.")

        
        # return number of batch steps
        return({"batch_size":(date_stop - date_start)/step_size,
                "step_size":step_size})
    
    def limit_check(self, add=1):
        """
        # function to make sure we do not exceed request limits of a thousand per minute

        
        Parameters:
        add (int) -  adds one per times we call the historical data retrieval function
        
        
        Returns:
        self.counter: updated count of calls and stops for one minute if %self.limit = 0

        """
        self.counter += add
        if self.counter%self.limit == 0:
            sleep(60)
        else:
            pass

    def db_update(self, coin, period_start, interval_id):
        """
        Retrieves new data and if not empty updates SQL data base
        
        Parameters:
        coin (str): string indicating they currency name
        period_start(str): Start datetime string e.g. "2019-03-12 12:30:45"
        interval_id(str): Interval resolution in minutes hours or days, permitted strings are '1d', '4h', '1h', '15m'
        host_info(str): VM address
        
        Returns:
        
        """
     
        data = self.retrieve_hist(coin = coin, period_start=period_start, interval_id=interval_id)

        # if we do not have any data to update we exit
        if len(data) == 0:
            logger.info(f"db_update: No data retrieved for coin {coin} with interval {interval_id} from {period_start}. Skipping update.")
            pass
        else:
            logger.info(f"db_update: Retrieved {len(data)} records for coin {coin} with interval {interval_id} from {period_start}. Proceeding with update.")
            # make elements numeric
            data = [[float(item) for item in sublist] for sublist in data]

            # transfrom data into numpy array so that it is more workable - use object array for mixed data
            data = np.array(data, dtype=object)

            # transform open and close time to standard datetime format
            data[:,0] = self.unix_to_datetime(data[:,0])
            data[:,6] = self.unix_to_datetime(data[:,6])

            # drop the last column, does not contain important info
            data = np.delete(data, -1, 1)

            """ write data into tables"""

            #connect database
            conn = get_connection()
            if conn is None:
                logger.error("retrieve_hist: Failed to connect to the database.")
                return
            # If the connection is successful, proceed with the database operations
            
            # next create a cursor
            cur = conn.cursor()

            '''
            # insert the primary keys coin
            cur.execute("""
            INSERT INTO Crypto_ID (Crypto_name)
            SELECT %s
            WHERE NOT EXISTS (
                SELECT 1 FROM Crypto_ID 
                WHERE Crypto_name = %s
            );""", (self.coin, self.coin))

            # insert the primary keys interval
            cur.execute("""INSERT INTO Interval_ID (Interval_name)
            SELECT %s
            WHERE NOT EXISTS (
                SELECT 1 FROM Interval_ID 
                WHERE Interval_name = %s
            );""", (self.interval, self.interval))

            #commit changes
            conn.commit()
            '''
            # get interval id
            cur.execute("""SELECT id
                            FROM interval i
                            WHERE i.name_short = %s""", [self.interval_id])
            ids = cur.fetchone()
            if ids == None:
                logger.error(f"retrieve_hist: Interval {self.interval_id} not found in the database.")
                return
            else:
                use_interval_id = ids[0]
            logger.debug(f"retrieve_hist: Interval {self.interval_id} found in the database with id {use_interval_id}.")

            # get crypto id
            cur.execute("""SELECT id
                            FROM crypto_coin cc
                            WHERE cc.ticker = %s""", [self.coin])
            ids = cur.fetchone()
            if ids == None:
                logger.error(f"retrieve_hist: Coin {self.coin} not found in the database.")
                return
            else:
                use_coin_id = ids[0]
            logger.debug(f"retrieve_hist: Coin {self.coin} found in the database with id {use_coin_id}.")

            # create array with currency name
            np_cur = np.concatenate((
                np.tile(use_coin_id, (data.shape[0], 1)),  
                np.tile(use_interval_id, (data.shape[0], 1)),
                np.tile(self.currency, (data.shape[0], 1))   
            ), axis=1)  # Concatenate along columns

            logger.debug("Get Data 1")

            # concatenate with the data array
            full_df = np.concatenate((np_cur, data), axis = 1)

            # remove columns 2, 10, 11, 12,13
            full_df = np.delete(full_df, [2, 10, 11, 12, 13], axis=1)
            
            csv_data = StringIO()
            np.savetxt(csv_data, full_df, delimiter='|', fmt='%s')  # Change delimiter to pipe
            csv_data.seek(0)

            logger.debug("Get Data 2")

#            cur.copy_from(
#                csv_data,
#                'crypto_coin_candle',
#                sep='|',  # Match the delimiter you used above
#                columns=('crypto_id', 'interval_id', 'currency_name', 'open_time',
#                        'open_price', 'close_price', 'high_price', 'low_price',
#                        'volume', 'close_time',  'quote_asset_volume', 'nr_trades',
#                        'tb_based_asset_volume', 'tb_quote_asset_volume'))
 
            cur.copy_from(
                csv_data,
                'crypto_coin_candle',
                sep='|',  # Match the delimiter you used above
                columns=('crypto_id', 'interval_id', 'open_time',
                        'open_price', 'high_price', 'low_price','close_price',
                        'volume', 'close_time'))
            
            logger.debug("Get Data 3")

            # Commit the transaction
            conn.commit()

            # Close the connection
            cur.close()
            '''
            close_connection()
            '''

    def hist_update(self, time_stamp, period_start):
        """
        Initializes functions to retrieve and update database
        
        Parameters:
        time_stamp (str): datetime string of current retrieval e.g. "2019-03-12 12:30:45"
        period_start(str): Start datetime string e.g. "2019-03-12 12:30:45"
                
        Returns:
        
        """

        # record the retrieval update time and if necessary update the start date
        #TODO: make sure that the period_start is not before the last entry in the DB
        #period_start = self.record_retrieval_db_update(time_stamp, period_start)

        # 

        # loop through coins and intervals
        for coin in self.coin_list:
            logger.info(f"hist_update: Updating historical data for coin {coin} starting from {period_start}.")
            for interval in self.interval_list:
                self.db_update(coin = coin, 
                               period_start = period_start, 
                               interval_id = interval)
        
                

    def record_retrieval_db_update(self, timestamp, period_start):
        """
        Updates the Update_Record DB once. Also checks if DB is empty and if not 
        returns the last entry as the new period_start date
        
        
        Parameters:
        time_stamp (str): datetime string of current retrieval e.g. "2019-03-12 12:30:45"
        period_start(str): Start datetime string e.g. "2019-03-12 12:30:45"
        host_info(str): VM address
        
        Returns:
        period_start(str): Start datetime string if DB empty returns input, else last DB entry
        
        """
        conn = get_connection()
        if conn is None:
            logging.error("record_retrieval_db_update: Failed to connect to the database.")
            return period_start
        # If the connection is successful, proceed with the database operations
        
        # next create a cursor
        cur = conn.cursor()

        # Check if DB is empty
        cur.execute("""
        SELECT * FROM historical_data ;""") 
        content = cur.fetchall()

        if len(content) != 0:
            period_start = content[-1][1].strftime("%Y-%m-%d %H:%M:%S")

        # record retrieval date
        cur.execute("""
        INSERT INTO historical_data (updated_at)
        VALUES (%s);""", (timestamp,)) 

        # Commit the transaction
        conn.commit()

        # Close the connection
        cur.close()
        close_connection()

        return(period_start)


                

