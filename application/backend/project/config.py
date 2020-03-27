import os
import logging

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
DATABASE_URL = f'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/geoquiz'

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
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = DATABASE_URL