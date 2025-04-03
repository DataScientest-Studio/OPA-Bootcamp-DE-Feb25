import requests
import json
from datetime import datetime
from time import sleep
from functools import wraps
import inspect
from math import floor
import pandas as pd
import psycopg2
import numpy as np
from io import StringIO


class retrieval():
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
        symbol = coin + currency

        #base_url = "http://api.coincap.io/v2/assets/bitcoin/history"
        base_url = "https://api.binance.com/api/v3/klines"

        # update counter to not exceed binance limits:
        self.limit_check()
        
        # Parameters - using a dictionary makes it cleaner
        params = {
            "symbol": symbol,
            "interval": self.interval,
            "startTime": period_start,
            "endTime": period_end,
            "limit":    self.limit
        }

        response = requests.get(base_url, params=params)

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
        self.interval_id (str) -  Interval resolution in minutes hours or days, permitted strings are '1d', '4h', '1h', '15m'
        self.date_stop (int) - Start datetime string transformed to Unix time
        
        Returns:
        dict: returns dictionary with the total batch size and the step size
        """
        
        if self.interval_id[-1]== 'm':
            step_size = 60*1000*int(self.interval_id[:-1])
        elif self.interval_id[-1]== 'h':
            step_size = 60*60*1000*int(self.interval_id[:-1])
        elif self.interval_id[-1]== 'd':
            step_size = 24*60*60*1000*int(self.interval_id[:-1])

        
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

    def db_update(self, coin, period_start, interval_id,  time_stamp, host_info):
     
        data = self.retrieve_hist(coin = coin, period_start=period_start, interval_id=interval_id)

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
        conn = psycopg2.connect(database="crypto_db",
                                host=host_info,
                                user="daniel",
                                password="datascientest",
                                port=5432)
        
        # next create a cursor
        cur = conn.cursor()

        # record retrieval date
        cur.execute("""
        INSERT INTO Update_Record (Update_date)
        VALUES (%s);""", (time_stamp,)) 

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

        # same for interval
        cur.execute("""SELECT Interval_ID
                        FROM Interval_ID
                        WHERE Interval_name = %s""", [self.interval])
                
        # get id
        interval_id = cur.fetchone()

        # same for crypto
        cur.execute("""SELECT Crypto_ID
                        FROM Crypto_ID
                        WHERE Crypto_name = %s""", [self.coin])

        # get id
        Coin_id = cur.fetchone()



        # create array with currency name
        np_cur = np.concatenate((
            np.tile(Coin_id, (data.shape[0], 1)),  
            np.tile(interval_id, (data.shape[0], 1)),  
            np.tile(self.currency, (data.shape[0], 1))   
        ), axis=1)  # Concatenate along columns

        # concatenate with the data array
        full_df = np.concatenate((np_cur, data), axis = 1)

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

    def hist_update(self, time_stamp, host_info, period_start):

        # loop through coins and intervals
        for coin in self.coin_list:
            print(coin)
            for interval in self.interval_list:
                self.db_update(coin = coin, 
                               period_start = period_start, 
                               interval_id = interval,  
                               time_stamp = time_stamp, 
                               host_info = host_info)


                

