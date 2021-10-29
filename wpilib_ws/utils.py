import sys
import logging


def setup_default_logger():

    logger = logging.getLogger("wpilib-ws")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger
