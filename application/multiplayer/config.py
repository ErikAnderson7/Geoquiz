import os
import logging

logging.basicConfig(level=logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] (%(filename)s | %(funcName)s) %(message)s")
LOG = logging.getLogger()
LOG.handlers.clear()

fileHandler = logging.FileHandler('/var/log/geoquiz.log')
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)

LOG.addHandler(fileHandler)
LOG.addHandler(consoleHandler)

class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    TESTING = True

class ProductionConfig(BaseConfig):
    """Production configuration"""
