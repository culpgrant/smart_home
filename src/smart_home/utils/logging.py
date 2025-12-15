"""Utils for logging for smart_home."""

import logging
import sys

# Define a standard format for all logs
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def get_logger() -> logging.Logger:
    """Creates default logger for smart_home.

    Returns:
        logging.Logger: Default Logger
    """
    # 1. Get the root logger
    root_logger = logging.getLogger()

    if root_logger.level == logging.NOTSET:
        root_logger.setLevel(logging.INFO)

    # Check if handlers have already been set up to prevent duplicates
    if root_logger.handlers:
        return root_logger

    # 2. Set the global log level
    root_logger.setLevel(logging.INFO)

    # 3. Create the Handler (e.g., to send logs to the console/stderr)
    handler = logging.StreamHandler(sys.stderr)

    # 4. Create the Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)

    # 5. Add the handler to the root logger
    root_logger.addHandler(handler)

    return root_logger
