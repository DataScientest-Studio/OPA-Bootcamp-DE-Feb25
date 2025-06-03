from flask import Flask
from sqlalchemy import inspect

from .definition import api
from .definition import db
from .definition import swagger
from .routes import api_register_routes
from ..DB import seed_data

import logging

logger = logging.getLogger(__name__) 

def create_app(config_class='config.PostgresqlConfig'):
#def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.app_context().push()
    app.config.from_object(config_class)
    
    db.init_app(app)
    api_register_routes(api)
    swagger.init_app(app)
    api.init_app(app)

    inspector = inspect(db.engine)
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.get_table_names():
            logger.info("No tables found in the database - re-create all tables.")
            db.create_all()
        else:
            logger.info("Database tables already exist - no need to re-create.")
        logger.info("Seeding initial data into the database (only if not exist).")
        #TODO disabled
        #seed_data(db)

    return app



