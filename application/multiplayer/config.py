import os
import logging
from pymongo import MongoClient

mongo_user = os.environ.get('MONGODB_USER')
mongo_password = os.environ.get('MONGODB_PASSWORD')

mongoConnectionURL = f'mongodb://{mongo_user}:{mongo_password}@multiplayer-db:27017'
mongo = MongoClient(mongoConnectionURL)
db=mongo.multiplayergames

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
