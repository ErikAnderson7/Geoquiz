from flask import Blueprint, jsonify, request
import project.geodata as gd
import pandas
import numpy as np
import random
import math
from sqlalchemy import func, asc
from project.config import LOG
from project import db
from project.guesses import Guess

stats_blueprint = Blueprint('stats', __name__)

# Clears the databases and repopulates it with 10000 guesses.
# Delete this method when done with dev work
@stats_blueprint.route("/populate")
def populate_db():
    LOG.info("Clearing database of guesses")
    guesses_deleted = db.session.query(Guess).delete()
    db.session.commit()
    LOG.info("Guesses deleted: " + str(guesses_deleted))
    for i in range(0, 10000): # Populate database with 10000 guesses
        if i % 10 == 0: # Every tenth guess generated is a correct guess
            LOG.info(str(i) + " Creating a correct guess")
            country_id = random.randrange(177) # 177 is number of countries
            db.session.add(Guess(correctcountry=country_id, guesscountry=country_id))
        else:
            LOG.info(str(i) + " Creating a random guess")
            country_id = random.randrange(177)
            guess_id = random.randrange(177)
            db.session.add(Guess(correctcountry=country_id, guesscountry=guess_id))
    db.session.commit()
    LOG.info("Finished Creating new guesses")

    df = getCorrectCountryDF(4)
    getGuessedCountryDF(4)

    calculateStats(df)

    return jsonify({'status': 'success!'})

# Queries database for guesses where country_id was the correct country
# Converts the query to a pandas dataframe with correctcountry, guesscountry, and count columns
def getCorrectCountryDF(country_id):
    country_query = db.session.query(Guess.correctcountry, Guess.guesscountry, func.count(Guess.guesscountry).label('count')) \
        .filter(Guess.correctcountry == country_id) \
        .group_by(Guess.guesscountry, Guess.correctcountry) \
        .order_by(asc(Guess.guesscountry)) \
        .statement
    df = pandas.read_sql_query(country_query, db.session.bind)
    LOG.info(df.head())
    return df

# Queries database for guesses where guessed_id was the country the user guessed
# Converts the query to a pandas dataframe with correctcountry, guesscountry, and count columns
def getGuessedCountryDF(guessed_id):
    guess_query = db.session.query(Guess.guesscountry, Guess.correctcountry, func.count(Guess.correctcountry).label('count')) \
        .filter(Guess.guesscountry == guessed_id) \
        .group_by(Guess.correctcountry, Guess.guesscountry) \
        .order_by(asc(Guess.correctcountry)) \
        .statement
    df = pandas.read_sql_query(guess_query, db.session.bind)
    LOG.info(df.head())
    return df

def getGlobalDF():
    global_query = db.session.query(Guess).statement
    df = pandas.read_sql_query(global_query, db.session.bind)
    LOG.info(df.head())
    return df

def calculateStats(df):
    cdf = gd.openGeoData()
    # Calculate distance between correct country and guess country for each row (axis=1)
    df['distance'] = df.apply(lambda x: gd.calcDistance(cdf, x['correctcountry'], x['guesscountry']), axis=1) 
    
    total_guesses = df['count'].sum()
    LOG.info("Total Guesses: " + str(total_guesses))
    df['percentOfGuesses'] = df.apply(lambda x: float(x['count'] / total_guesses) * 100, axis=1)

    LOG.info(df.head())