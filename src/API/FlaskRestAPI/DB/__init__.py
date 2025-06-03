from .cryptocoincandle import CryptoCoinCandle
from .interval import Interval
from .cryptocoin import CryptoCoin
from .historicaldata import HistoricalData
from .info import Info

import logging

logger = logging.getLogger(__name__) 

def seed_data(db):
    from .interval import IntervalModel
    from .cryptocoin import CryptoCoinModel

    # Check if Interval data already exists
    logger.info("Checking if initial Interval data exists in the database .")
    if IntervalModel.query.first() is None:
        intervals = [
            IntervalModel(name_long="One week", name_short="1w"),
            IntervalModel(name_long="One day", name_short="1d"),
            IntervalModel(name_long="One hour", name_short="1h"),
        ]
        db.session.add_all(intervals)
        db.session.commit()
        logger.info("Initial Interval data seeded into the database.")
    
    # Check if CryptoCoin data already exists
    logger.info("Checking if initial CryptoCoin data exists in the database.")
    if CryptoCoinModel.query.first() is None:
        cryptocoins = [
            CryptoCoinModel(name="BTCTUSD", ticker="BTC"),
            CryptoCoinModel(name="XRPTUSD", ticker="XRP"),
            CryptoCoinModel(name="PEPETUSD", ticker="PEPE"),
        ]
        db.session.add_all(cryptocoins)
        db.session.commit()
        logger.info("Initial CryptoCoin data seeded into the database.")
