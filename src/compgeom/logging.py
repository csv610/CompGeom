"""Standardized logging for the CompGeom project."""

import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Returns a logger with a consistent configuration.

    Args:
        name: The name of the logger (usually __name__).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
