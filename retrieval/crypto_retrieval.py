import requests
import json

class retrieval():
    def __init__(self):
        self.something =1

    # main functions

    def retrieve_hist(self, coin_id=[], market_id=[], interval_id="d1", period_start, period_end):
        """
        Retrieves data for specified coins at specific markets
        
        Parameters:
        coin_id (str): string indicating they currency name
        market_id (str): string indicating they exchange name
        period_start (str): Start datetime string e.g. "2019-03-12 12:30:45"
        period_end (str): End datetime string e.g "2025-03-12 12:30:45"
        
        Returns:
        data: JSON file format data
        """
        date_start = datetime_to_unix(period_start)
        date_stop = datetime_to_unix(period_end)

        base_url = "http://api.coincap.io/v2/assets/bitcoin/history"

        # Parameters - using a dictionary makes it cleaner
        params = {
            "interval": interval_id,
            "start": date_start*1000,
            "end": date_stop*1000
        }

        # Retrieve historical data
        response = requests.get(base_url, params=params)

        hist_data = json.loads(response.text)
        return(hist_data)




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
    def datetime_to_unix(dt_str, format_str='%Y-%m-%d %H:%M:%S'):
        """
        Convert a datetime string to Unix timestamp
        
        Parameters:
        dt_str (str): Datetime string to convert
        format_str (str): Format of the input datetime string
        
        Returns:
        int: Unix timestamp in seconds
        """
        # Parse the datetime string to a datetime object
        dt_object = datetime.strptime(dt_str, format_str)
        
        # Convert to Unix timestamp (seconds since epoch)
        unix_time = int(dt_object.timestamp())
        
        return unix_time
    
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
    
    def get_exchange_names(self):
        """
        Retrieve names of available exchanges on coin cap
        
        Parameters:

        
        Returns:
        list: returns list of exhcange names
        """

        url = "http://api.coincap.io/v2/exchanges"
        data = self.request_fun(url_str=url)
        ex_names = [ex_data['exchangeId'] for ex_data in data['data']]
        return(ex_names)
    