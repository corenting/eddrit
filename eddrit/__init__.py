import sys

from loguru import logger

from eddrit import config

__version__ = "0.8.1"

logger.remove()
logger.add(sys.stderr, level=config.LOG_LEVEL)
