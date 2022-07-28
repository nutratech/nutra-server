"""Logging module, generates a logger object for other modules in the API"""
import logging

from ntserv.env import LOG_LEVEL

FMT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)\n"


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger.
    Configure NTSERV_LOG_LEVEL in `.env` to filter logs.

    10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL
    """

    print(f"Returning a logger with level {LOG_LEVEL}")
    logging.basicConfig(level=LOG_LEVEL, format=FMT)
    return logging.getLogger(name)
