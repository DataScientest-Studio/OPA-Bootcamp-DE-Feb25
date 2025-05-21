import logging
from logging.handlers import RotatingFileHandler
import os
from config import config as cfg

def setup_logger(config):

    # Create a logs folder if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # Get from config
    LOG_APP = config['logging']['log_app']
    LOG_FILE = config['logging']['log_file']
    LOG_LEVEL = config['logging']['log_level']
    LOG_FORMAT = config['logging']['log_format']
    LOG_DATE_FORMAT = config['logging']['log_date_format']
    LOG_MAX_BYTES_SIZE = config.getint('logging','log_max_bytes_size')
    LOG_BACKUP_COUNT = config.getint('logging','log_backup_count')

    # Create rotating file handler (max 5 files, 1MB each)
    file_handler = RotatingFileHandler(LOG_FILE,
                                    maxBytes=LOG_MAX_BYTES_SIZE,
                                    backupCount=LOG_BACKUP_COUNT)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT,
                                                LOG_DATE_FORMAT))

    # Set up logger
    logger = logging.getLogger(LOG_APP)
    
    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(LOG_LEVEL)  # Set minimum logging level
    logger.addHandler(file_handler)

    # Optional: Add console handler for debugging
    #console_handler = logging.StreamHandler()
    #console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    #logger.addHandler(console_handler)
    return logger

logger = setup_logger(config=cfg)
