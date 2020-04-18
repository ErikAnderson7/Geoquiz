from flask import Blueprint, jsonify, request
import project.geodata as gd
import pandas
import geopandas
import numpy as np
import random
import math
from sqlalchemy import func, asc
from project.config import LOG
from project import db
from project.guesses import Guess

stats_blueprint = Blueprint('stats', __name__)

# Clears the databases and repopulates it with guess_count guesses.
# Delete this method when done with dev work
@stats_blueprint.route("/populate")
def populate_db():
    guess_count = request.args.get('guesses', default=100000, type = int)
    LOG.info("Clearing database of guesses")
    guesses_deleted = db.session.query(Guess).delete()
    db.session.commit()
    LOG.info("Guesses deleted: " + str(guesses_deleted))
    LOG.info("Generating " + str(guess_count) + " guesses")
    for i in range(0, guess_count): # Populate database with 10000 guesses
        if i % 10 == 0: # Every tenth guess generated is a correct guess
            country_id = random.randrange(176) # 176 is number of countries 0 indexed
            db.session.add(Guess(correctcountry=country_id, guesscountry=country_id))
        else:
            country_id = random.randrange(176)
            guess_id = random.randrange(176)
            db.session.add(Guess(correctcountry=country_id, guesscountry=guess_id))
    db.session.commit()
    LOG.info("Finished Creating new guesses")

    return jsonify({'status': 'success!'})

@stats_blueprint.route("/whenCorrectMap")
def getCorrectCountryMap():
    country_id = request.args.get('cid', default=0, type = int)
    LOG.info("Getting stats for country: " + str(country_id))
    
    stats_df = getCorrectCountryDF(country_id)
    geodata_df = gd.openGeoData()

    # Combine stats and geodata dataframes by using guesscountry as the key
    combined_df = stats_df.join(geodata_df.set_index('id'), on='guesscountry')
    combined_gdf = geopandas.GeoDataFrame(combined_df)

    # When displaying the map these columns are not needed
    combined_gdf = combined_gdf.drop(column=['guesscountry', 'correctcountry'])

    LOG.info(combined_gdf.head())

    combined_json = combined_gdf.to_json()
    return jsonify(combined_json)

@stats_blueprint.route("/whenCorrect")
def getCorrectCountryStats():
    country_id = request.args.get('cid', default=0, type = int)

    #operate on df to extract average distance of guesses, most commonly confused etc.


    stats = {
        "timesGuessedCorrectly": 0,
        "totalGuesses": 0,
        "percentGuessedCorrectly": 0.0,
        "averageDistance": 0,
        "mostCommonlyConfused": {
            "1st": {"name": "a", "times": 0, "percentage": 0.0},
            "2nd": {"name": "b", "times": 0, "percentage": 0.0},
            "3rd": {"name": "c", "times": 0, "percentage": 0.0},
            "4th": {"name": "d", "times": 0, "percentage": 0.0},
            "5th": {"name": "e", "times": 0, "percentage": 0.0}
        }        
    }

    return jsonify({"stats": "here"})

# Queries database for guesses where country_id was the correct country
# Converts the query to a pandas dataframe with correctcountry, guesscountry, and count columns
def getCorrectCountryDF(country_id):
    # SQLAlchemy Query 
    # SELECT correctcountry, guesscountry, count(guesscountry) from guesses where correctcountry = country_id group by guesscountry, correctcountry order by guesscountry asc;
    country_query = db.session.query(Guess.correctcountry, Guess.guesscountry, func.count(Guess.guesscountry).label('count')) \
        .filter(Guess.correctcountry == country_id) \
        .group_by(Guess.guesscountry, Guess.correctcountry) \
        .order_by(asc(Guess.guesscountry)) \
        .statement
    df = pandas.read_sql_query(country_query, db.session.bind)
    df = calculateStats(df) # Add the other statistics to the dataframe
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
    return df

def getGlobalDF():
    global_query = db.session.query(Guess).statement
    df = pandas.read_sql_query(global_query, db.session.bind)
    return df

def calculateStats(df):
    cdf = gd.openGeoData()
    # Calculate distance between correct country and guess country for each row (axis=1)
    df['distance'] = df.apply(lambda x: gd.calcDistance(cdf, x['correctcountry'], x['guesscountry']), axis=1) 
    
    # Calculate the percentage of guesses for each country
    total_guesses = df['count'].sum()
    LOG.info("Total Guesses: " + str(total_guesses))
    df['percentOfGuesses'] = df.apply(lambda x: float(x['count'] / total_guesses) * 100, axis=1)

    return df