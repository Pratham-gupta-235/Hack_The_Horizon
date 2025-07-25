# src/shared/utils.py

import psutil
import logging

def check_memory_usage() -> float:
    """
    Return the current system memory usage as a percentage (0-1).
    """
    return psutil.virtual_memory().percent / 100.0

def setup_logging(name: str = __name__, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


