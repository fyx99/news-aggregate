import logging
import os

#basic config for root logger - info to prevent moduls from spamming
# set this to info and get lots of bullshit from third party libs
logging.basicConfig(level=logging.ERROR, format="%(asctime)s.%(msecs)03d %(levelname)-5s %(threadName)-7s %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

log_level = os.environ.get("LOG_LEVEL", default="DEBUG")

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    return logger