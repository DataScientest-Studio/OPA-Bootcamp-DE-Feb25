from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

app_version = "1.0.1"

api = Api()
db = SQLAlchemy()
swagger = Swagger()