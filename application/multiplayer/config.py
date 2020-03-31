import os
import logging

logging.basicConfig(level=logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] (%(filename)s) %(message)s")
LOG = logging.getLogger()
LOG.handlers.clear()

fileHandler = logging.FileHandler('/var/log/geoquiz.log')
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)

LOG.addHandler(fileHandler)
LOG.addHandler(consoleHandler)

class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False

class DevelopmentConfig(BaseConfig):
    """Development configuration"""

class ProductionConfig(BaseConfig):
    """Production configuration"""
