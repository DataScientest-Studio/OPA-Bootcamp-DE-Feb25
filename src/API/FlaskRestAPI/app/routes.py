from FlaskRestAPI.DB.interval import Interval
from FlaskRestAPI.DB.interval import Intervals
from FlaskRestAPI.DB.historicaldata import HistoricalData
from FlaskRestAPI.DB.cryptocoin import CryptoCoin
from FlaskRestAPI.DB.cryptocoin import CryptoCoins
from FlaskRestAPI.DB.cryptocoincandle import CryptoCoinCandle
from FlaskRestAPI.DB.info import Info
from FlaskRestAPI.DB.models import MLModel
from FlaskRestAPI.DB.models import MLModels

_routes_registered = False

def api_register_routes(api):
    global _routes_registered
    if _routes_registered:
        return  # Skip if routes already registered
    
    # GET, PATCH, DELETE
    api.add_resource(Interval, "/opa/intervals/<int:interval_id>")
    # GET, POST, DELETE
    api.add_resource(Intervals, "/opa/intervals")

    # GET, POST
    api.add_resource(HistoricalData, "/opa/historicaldata")
    
    # GET, PATCH, DELETE
    api.add_resource(CryptoCoin, "/opa/cryptocoins/<int:crypto_id>")
    # GET, POST, DELETE
    api.add_resource(CryptoCoins, "/opa/cryptocoins")

    # GET, POST
    api.add_resource(CryptoCoinCandle, "/opa/candels")

    # POST
    api.add_resource(MLModel, "/opa/predict")

    # POST
    api.add_resource(MLModels, "/opa/models")

    # GET Info
    api.add_resource(Info, "/opa/info")

    _routes_registered = True


#TBD in API
#     load a model
#     store a model
#     currancy 
