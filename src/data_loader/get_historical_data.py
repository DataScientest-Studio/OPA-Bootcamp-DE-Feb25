import sys
from datetime import datetime
import time
import logging

from retrieval.crypto_retrieval import retrieval_handler

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__) 

time_start = time.time()
# initialize class
logging.info("Initializing retrieval handler for historical data")
ret = retrieval_handler(coin_list = ["BTC", "XRP", "PEPE"], interval_list = ["1h","1d", "1w"])

# save time at which we retriev data
update_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# retrieva data
startDate = "2024-05-01 00:00:00"
endDate = "2024-12-31 23:59:59"
interval = "1h"

logging.info(f"Retrieving historical coin data : start ->  {startDate}, end -> {endDate}, interval -> {interval}")
#data = ret.retrieve_hist(period_start=startDate,period_end=endDate, interval_id="1h")

# update historical tables 
logging.info(f"Update historical data:  date  {endDate}")
ret.hist_update(period_start="2024-05-01 00:00:00",time_stamp=update_stamp)

time_stop = time.time()

logging.info(f"Execution time in total: {time_stop-time_start} seconds")
if __name__ == "__main__":
    # This block is executed when the script is run directly
    logging.info("Script executed directly, running main code.")
