import logging
import pytest

from FlaskRestAPI.app import create_app
from FlaskRestAPI.app.definition import db

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.DEBUG,  
        format=log_format,
        handlers=[
            logging.FileHandler("logs/pytest.log", mode="w"),
            logging.StreamHandler()
        ]
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)  

@pytest.fixture
def app():
    app = create_app("config.TestConfig")  # Use your test config class
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()