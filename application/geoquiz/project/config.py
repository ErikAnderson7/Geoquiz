import os
import logging

# Postgres DB connection details
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
DATABASE_URL = f'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/geoquiz'

# Basic logging config
logging.basicConfig(level=logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] (%(filename)s | %(funcName)s) %(message)s")
LOG = logging.getLogger()
LOG.handlers.clear()

# File logging handler
fileHandler = logging.FileHandler('/var/log/geoquiz.log')
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)

# Console logging handler
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)

LOG.addHandler(fileHandler)
LOG.addHandler(consoleHandler)

class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    DEBUG = True
    TESTING = True

class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = DATABASE_URL