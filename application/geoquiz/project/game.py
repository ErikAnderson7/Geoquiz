from flask import Blueprint, jsonify, request
import project.geodata as gd
import random
import math
from project.config import LOG
from project import db
from project.guesses import Guess

game_blueprint = Blueprint('game', __name__)

# Gets a new question by randomly selecting a country id
@game_blueprint.route("/getQuestion")
def getQuestion():
    geodataDF = gd.openGeoData()
    countryCount = geodataDF.shape[0] # Number of countries in the dataframe
    
    countryid = random.randint(0, countryCount)
    country = gd.lookupCountryName(countryid)
    
    response = {'Country': country}
    LOG.info("Getting a new question: " + str(response))

    return jsonify(response)

# Checks a user's answer. 
# Guess is the id of the country the user clicked on
# Country is the correct country.
@game_blueprint.route("/checkAnswer")
def checkAnswer():
    correctCountry = request.args.get('country', default='NONE', type = str)
    guessCountryid = request.args.get('guess', default = 0, type = int)
    
    correctCountryid = gd.lookupCountryID(correctCountry)
    guessCountry = gd.lookupCountryName(guessCountryid)

    LOG.info("Checking an answer Correct Country: " + correctCountry + " User's Guess: " + guessCountry)
    LOG.info("Checking an answer Correct Country ID: " + str(correctCountryid) + " User's Guess ID: " + str(guessCountryid))
    
    # Insert the guess into the database
    LOG.debug("Inserting the guess into the databse")
    userGuess = Guess(correctcountry=correctCountryid, guesscountry=guessCountryid)
    db.session.add(userGuess)
    db.session.commit()
    LOG.debug("Insertion complete")

    if guessCountryid == correctCountryid:
        response = {'Correct' : 'True'}
    else:
        geodataDF = gd.openGeoData()
        distance = gd.calculateDistance(geodataDF, correctCountryid, guessCountryid)
        response = {'Correct' : 'False', 'CorrectID' : correctCountryid, 'Guess' : guessCountry, 'Distance' : int(distance)}
    
    return jsonify(response)

# Returns the GeoJSON data for the entire world
@game_blueprint.route("/getGameMap")
def gameMap():
	LOG.info("Getting the world map")
	countries_df = gd.getGameWorldData()
	return jsonify(countries_df.to_json())

# Returns the GeoJSON data for a specific country
@game_blueprint.route("/getCountryMap")
def countryMap():
	country = request.args.get('i', default=0, type = int)
	LOG.info("Getting country: " + str(country))
	return jsonify(gd.getCountry(country).to_json())