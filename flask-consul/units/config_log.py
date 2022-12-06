from config import log_level
import sys
from loguru import logger
logger.remove()
logger.add(sys.stderr,format='<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>',level=log_level)
