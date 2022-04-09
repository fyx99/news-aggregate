import logging
import os

#basic config for root logger - info to prevent moduls from spamming
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

log_level = os.environ.get("LOG_LEVEL", default="DEBUG")

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    return logger