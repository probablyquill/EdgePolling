import logging
from logging.handlers import RotatingFileHandler

# Quick init function for setting up a logger inside of a module. Only needs to be called at the top level,
# or if a module is being run on its own.
file_name = "default"

# log = logging.getLogger(__name__)
# log.setLevel(logging.INFO)

def init(file_name):
    file_name = file_name
    logging.basicConfig(
    handlers=[RotatingFileHandler(f"./logs/{file_name}.log", maxBytes=100000, backupCount=10)],
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt='%Y-%m-%dT%H:%M:%S')

    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)