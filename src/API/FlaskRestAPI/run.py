import logging
import sys

from FlaskRestAPI.app import create_app

# Set up centralized logging to be used with Docker logging 
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)