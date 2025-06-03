import requests
from datetime import datetime
import tzlocal

BASE = "http://127.0.0.1:5000/ope/"

'''
data = [{"name":"Maciej", "views":100, "likes":10},
        {"name":"Ola", "views":200, "likes":20},
        {"name":"Kuba", "views":300, "likes":30}]

for i in range(len(data)):
    response = requests.put(BASE +"video/" + str(i+3), json=data[i])
    print(response.json())

#, headers={"Content-Type":"application/json","charset":"utf-8"}
'''
print("\nHistoricalData - GET - all items")
response = requests.get(BASE + "historicaldata")
print(response.json())

print("\nHistoricalData - POST - add new item")
updated_at = {"updated_at": datetime.now(tzlocal.get_localzone()).isoformat()}
response = requests.post(BASE + "historicaldata", json=updated_at)
print(response.json())
######################################################
###     Intervals        #############################
######################################################
print("\nInterval - POST - three items added - OK")
intervals = [{"name_long":"one week", "name_short":"1w"},
            {"name_long":"one day", "name_short":"1d"},
            {"name_long":"one hour", "name_short":"1h"}]
response = requests.post(BASE +"intervals", json=intervals)
print(response.json())

print("\nInterval - GET - all interval items - OK")
response = requests.get(BASE + "intervals")
print(response.json())

print("\nInterval - GET - interval_id=3 - OK")
response = requests.get(BASE + "intervals/3")
print(response.json())

print("\nInterval - GET - interval_id=4 - NOK")
response = requests.get(BASE + "intervals/4")
print(response.json())

print("\nInterval - PATCH - interval_id=3, without data - NOK")
response = requests.patch(BASE + "intervals/3")
print(response.json())

######################################################
###     CryptoCoin       #############################
######################################################
print("\nCryptoCoin - DELETE - all items")
response = requests.delete(BASE + "cryptocoins")
print(response.json())

print("\nCryptoCoin - POST - 3 items, by the second  UNIQUE CONSTRAINT - NOK")
coins = [{"name":"BTCTUSD", "ticker":"BTC"},
        {"name":"BTCTUSD", "ticker":"PEP"},
        {"name":"XRPTUSDx", "ticker":"XRPx"}]
response = requests.post(BASE +"cryptocoins", json=coins)
print(response.json())

print("\nCryptoCoin - POST - 3 items, by the second  UNIQUE CONSTRAINT - NOK")
coins = [{"name":"BTCTUSD", "ticker":"BTC"},
        {"name":"BTCTEUR", "ticker":"PEP"},
        {"name":"XRPTUSDx", "ticker":"XRPx"}]
response = requests.post(BASE +"cryptocoins", json=coins)
print(response.json())

print("\nCryptoCoin - GET - all items")
response = requests.get(BASE + "cryptocoins")
print(response.json())

print("\nCryptoCoin - GET - crypto_id=1 - OK")
response = requests.get(BASE + "cryptocoins/1")
print(response.json())

###     CryptoCoin - PATCH      #############################

print("\nCryptoCoin - PATCH - crypto_id=5 does not exist")
update_coin = {"name": "XRPTUSD", "ticker":"XRP"}
response = requests.patch(BASE + "cryptocoins/5", json=update_coin)
print(response.json())

print("\nCryptoCoin - PATCH - name argument NOT provided")
update_coin = {"nameX": "XRPTUSD", "ticker":"XRP"}
response = requests.patch(BASE + "cryptocoins/3", json=update_coin)
print(response.json())

print("\nCryptoCoin - PATCH - ticker argument NOT provided")
update_coin = {"name": "XRPTUSD", "tickerX":"XRP"}
response = requests.patch(BASE + "cryptocoins/3", json=update_coin)
print(response.json())

print("\nCryptoCoin - PATCH - crypto_id=3 update OK")
update_coin = {"name": "XRPTUSD", "ticker":"XRP"}
response = requests.patch(BASE + "cryptocoins/3", json=update_coin)
print(response.json())

print("\nCryptoCoin - PATCH - crypto_id NOT provided")
update_coin = {"name": "XRPTUSD", "ticker":"XRP"}
response = requests.patch(BASE + "cryptocoins", json=update_coin)
print(response.json())

print("\nCryptoCoin - GET - all items")
response = requests.get(BASE + "cryptocoins")
print(response.json())

print("\nCryptoCoin - DELETE - crypto_id=3 item OK")
response = requests.delete(BASE + "cryptocoins/3")
print(response.json())

print("\nCryptoCoin - DELETE - crypto_id doesn't exist")
response = requests.delete(BASE + "cryptocoins/4")
print(response.json())

######################################################
###     CryptoCoinCandels     ########################
######################################################
arguments = {"ticker":"BTCTUSD", "startDate":"20001201000000", "interval":"1w"}
print("\nCryptoCoinCandle - GET - ticker NOT found")
response = requests.get(BASE + "candels?ticker=BTCTUSD&startDate=20001201000000&interval=1w")
print(response.json())

arguments = {"ticker":"BTC", "startDate":"200012010000", "interval":"1w"}
print("\nCryptoCoinCandle - GET - startDate ivalid format")
response = requests.get(BASE + "candels?ticker=BTC&startDate=200012010000&interval=1w")
print(response.json())

arguments = {"ticker":"BTC", "startDate":"20001201000000", "interval":"1ww"}
print("\nCryptoCoinCandle - GET - interval invalid value")
response = requests.get(BASE + "candels?ticker=BTC&startDate=20001201000000&interval=1ww")
print(response.json())

print("\nCryptoCoinCandle - POST - one record - OK")
candels = [{"crypto_id": 1, "interval_id": 1,"open_price":1.2, "close_price":1.31,
            "high_price": 1.4, "low_price":1.19,
            "volume": 1200.0, "close_time":"2025-04-28T13:38:01.180072+02:00"},
            {"crypto_id": 1, "interval_id": 1,"open_price":1.2, "close_price":1.31,
            "high_price": 1.4, "low_price":1.19,
            "volume": 1200.0, "close_time":"2025-04-27T13:38:01.180072+02:00"}]
response = requests.post(BASE + "candels", json=candels)
print(response.json())

print("\nCryptoCoinCandle - GET - no end Date all records")
response = requests.get(BASE + "candels?ticker=BTC&startDate=20001201000000&interval=1w")
print(response.json())

print("\nCryptoCoinCandle - GET - no end Date all records after 2025-05-28 00:00:00")
response = requests.get(BASE + "candels?ticker=BTC&startDate=20250428000000&interval=1w")
print(response.json())

print("\nCryptoCoinCandle - GET - all records between 2025-04-28 00:00:00 and 2025-04-29 23:59:59")
response = requests.get(BASE + "candels?ticker=BTC&startDate=20250428000000&endDate=20250429235959&interval=1w")
print(response.json())

##########################################################
##### Clear #######
print("\nInterval - DELETE - all items - OK")
response = requests.delete(BASE + "intervals")
print(response.json())

##########################################################
##### Info #######
print("\nInfo -  OK")
response = requests.get(BASE + "info")
print(response.json())

'''
BASE_BIONANCE = "https://data-api.binance.vision/"

response = requests.get(BASE_BIONANCE+"api/v3/time", {})
print(response.json())

response = requests.get(BASE_BIONANCE+"/api/v3/trades", {"symbol": "LTCBTC"})
print(response.json())
'''