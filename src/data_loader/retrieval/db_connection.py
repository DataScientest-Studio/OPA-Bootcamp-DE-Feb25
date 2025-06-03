import os
import psycopg2
from functools import lru_cache
import atexit

import logging

logger = logging.getLogger(__name__) 

@lru_cache(maxsize=1)
def get_connection():

    try:
        # Load environment variables for database connection
        # Ensure these are set in your environment or .env file before running the script
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = int(os.getenv("DB_PORT", 5432))
        
        logging.info(f"Connecting to the database: {DB_NAME} at {DB_HOST}:{DB_PORT} as user {DB_USER}")
        conn = psycopg2.connect(database=DB_NAME,
                                host=DB_HOST,
                                user=DB_USER,
                                password=DB_PASSWORD,
                                port=DB_PORT)
        logging.info(f"Succesfully connected to the database: {DB_NAME}")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return None

def close_connection():
    conn = get_connection
    try:
        conn.close()
        logging.info("Database connection closed.")
    except Exception as e:
        pass

atexit.register(close_connection)
