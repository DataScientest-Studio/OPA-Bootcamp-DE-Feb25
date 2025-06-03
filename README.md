# OPA_Project
Project were we stream crypto data and try to predict prices

API:
1. Build and start all Docker containers (docker-compose-opa.yaml)

2. Build a tunel from local PC

For FlaskAPI:
ssh -i "your.pem" -L 8088:localhost:8088 ubuntu@[current-ip]

For Streamlit dashboard:
ssh -i "your.pem" -L 8090:localhost:8090 ubuntu@[current-ip]

3. API docs:
http://localhost:8088/apidocs/

4. Streamlit dashboard
http://localhost:8090

Docs:

    Defence presentation: DataScientest-Project-OPA.pptx
    UML drawings: OPA-UML.drawio (open on draw.io)

Source code :

    1. API:
        src/API - FlaskAPI

    2. Streamlit:
        src/streamlit_app

    3. data loading:
        src/data_loader

    4. machine learning:
        src/ML
    
    5. docker-compose-opa.yaml - defines 6 containers
    6. .env - environment variables using by docker containers




