import logging
import os

# create logs folder outside reload tracking
LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(
    LOG_DIR,
    "app.log"
)

logger = logging.getLogger("app_logger")

logger.setLevel(logging.INFO)

# prevent duplicate handlers
if not logger.handlers:

    file_handler = logging.FileHandler(
        LOG_FILE
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    # stop console spam
    logger.propagate = False