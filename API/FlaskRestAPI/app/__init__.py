from flask import Flask

from .definition import api
from .definition import db
from .definition import swagger
from .routes import api_register_routes

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.app_context().push()
    app.config.from_object(config_class)
    
    db.init_app(app)
    swagger.init_app(app)
    api_register_routes(api)
    api.init_app(app)

    #Use it only once
    db.create_all()

    return app

