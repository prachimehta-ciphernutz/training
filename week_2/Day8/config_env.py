import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level = getattr(logging, LOG_LEVEL, logging.INFO),
    format = "%(asctime)s | %(levelname)s | %(message)s"
)

logging.debug("Debug log")
logging.info("Info log")