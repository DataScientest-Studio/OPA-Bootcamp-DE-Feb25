# OPA_Project
Project were we stream crypto data and try to predict prices

API:
1. Build a tunel from local PC
ssh -i "your.pem" -L 8088:localhost:8088 ubuntu@[current-ip]
2. start API
flask run --reload --host=0.0.0.0 --port=8088

3. API docs:
http://localhost:8088/apidocs/

