cd
cd OPA-Bootcamp-DE-Feb25

source ./opeenv/bin/activate
cd API/FlaskRestAPI

export FLASK_APP=run.py  # or your main file, e.g., run.py or app/__init__.py
export FLASK_ENV=development  # Optional: enables debug mode

flask run --reload --host=0.0.0.0 --port=8088