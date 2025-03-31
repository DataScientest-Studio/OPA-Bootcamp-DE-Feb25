import requests
import json
from datetime import datetime
from functools import wraps
import inspect
from math import floor

class retrieval():
    def __init__(self, limit = 1000):
        """
        Parameters:
        limit (int): Number of records to retrieve (max 1000)
        """
        self.limit = limit
        # Apply the decorator to the method after initialization
        self.retrieve_hist = self.batch_decorator(self.retrieve_hist)

    def batch_decorator(self, func):
    # Decorator that checks if batch size exceeds limit - if so calls retrieval multiple times
        @wraps(func)
        def wrapper(*args, **kwargs):

            # Extract parameters from kwargs or use defaults
            period_start = kwargs.get('period_start', [])
            period_end = kwargs.get('period_end', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.interval_id = kwargs.get('interval_id', "1d")
            
            # Set date attributes
            self.date_start = self.datetime_to_unix(period_start) * 1000
            self.date_stop = self.datetime_to_unix(period_end) * 1000

            #save once for final comparison
            self.final = self.datetime_to_unix(period_end) * 1000
            
            # Initialize variables
            results = []
            # call batch_info safely
            batch_info = self.batch_steps()
            
            print(batch_info)
            # Check if batching is needed
            if batch_info["batch_size"] < self.limit:  
                return func(*args, **kwargs)
            
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Calculate number of calls needed
            call_nr = floor(batch_info['batch_size']/self.limit)
            print(call_nr)
    
            # Initialize start and end boundaries
            start = self.date_start
           
            
            # Loop to retrieve all batches
            for call in range(call_nr):
                print("A call made")
                bound_args.arguments['period_start'] = start
                end = start + batch_info['step_size'] * self.limit
                bound_args.arguments['period_end'] = end
                
                # Update self.date_start and self.date_stop before each call
                self.date_start = start
                self.date_stop = end
                

                # Call the original function with modified arguments
                
                batch_result = func(*bound_args.args, **bound_args.kwargs)
        
                if batch_result:  # Only append if there are results
                    results.append(batch_result)
                    
                # Update the new start point
                start = end 
    
            
            # Check if we need a final call for remaining data
            
            if start < self.final:
                print("final stop not reached")
                bound_args.arguments['period_start'] = start
                end = self.final
                bound_args.arguments['period_end'] = end
                
                # Update self.date_start and self.date_stop before each call
                self.date_start = start
                self.date_stop = end
                

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
    def retrieve_hist(self, symbol='BTCUSDT', interval_id="1d", period_start= [] , period_end=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
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

        #base_url = "http://api.coincap.io/v2/assets/bitcoin/history"
        base_url = "https://api.binance.com/api/v3/klines"

        """ # Parameters - using a dictionary makes it cleaner - dictionary is for coinCap
        params = {
            "interval": interval_id,
            "start": date_start*1000,
            "end": date_stop*1000
        } """
        # save final stop
        self.fin_stop = self.datetime_to_unix(period_end)
        # Parameters - using a dictionary makes it cleaner
        params = {
            "symbol": symbol,
            "interval": self.interval_id,
            "startTime": self.date_start,
            "endTime": self.date_stop,
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
    
    def batch_steps(self):
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
        return({"batch_size":(self.date_stop - self.date_start)/step_size,
                "step_size":step_size})
    