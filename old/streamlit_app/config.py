import configparser
import os

CONFIG_FILE_NAME = 'config.ini'
# Load config.ini
config = configparser.ConfigParser(interpolation=None)
config_file = os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)
config.read(config_file)

# Database Config
DB_HOST = config['database']['host']
DB_PORT = config.getint('database', 'port')
DB_USER = config['database']['user']
DB_PASSWORD = config['database']['password']
DB_NAME = config['database']['database']
