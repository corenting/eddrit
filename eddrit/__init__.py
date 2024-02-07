import sys

from loguru import logger

from eddrit import config

__version__ = "0.7.0"

logger.remove()
logger.add(sys.stderr, level=config.LOG_LEVEL)
