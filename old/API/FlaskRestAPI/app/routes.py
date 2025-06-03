from FlaskRestAPI.DB.interval import Interval
from FlaskRestAPI.DB.interval import Intervals
from FlaskRestAPI.DB.historicaldata import HistoricalData
from FlaskRestAPI.DB.cryptocoin import CryptoCoin
from FlaskRestAPI.DB.cryptocoin import CryptoCoins
from FlaskRestAPI.DB.cryptocoincandle import CryptoCoinCandle
from FlaskRestAPI.DB.info import Info

_routes_registered = False

def api_register_routes(api):
    global _routes_registered
    if _routes_registered:
        return  # Skip if routes already registered
    
    # GET, PATCH, DELETE
    api.add_resource(Interval, "/ope/intervals/<int:interval_id>")
    # GET, POST, DELETE
    api.add_resource(Intervals, "/ope/intervals")

    # GET, POST
    api.add_resource(HistoricalData, "/ope/historicaldata")
    
    # GET, PATCH, DELETE
    api.add_resource(CryptoCoin, "/ope/cryptocoins/<int:crypto_id>")
    # GET, POST, DELETE
    api.add_resource(CryptoCoins, "/ope/cryptocoins")

    # GET, POST
    api.add_resource(CryptoCoinCandle, "/ope/candels")

    # GET Info
    api.add_resource(Info, "/ope/info")

    _routes_registered = True

#TBD in API
#     load a model
#     store a model
#     currancy 
