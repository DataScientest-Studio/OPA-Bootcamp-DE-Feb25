echo -e "\n\n1. Test - OK\n"
curl -X GET "https://api.binance.com/api/v3/klines?symbol=PEPEUSDT&interval=1d&startTime=1735689600000&endTime=1748527700000&limit=1000"
echo -e "\n\n"