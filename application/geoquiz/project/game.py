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
    gpdf = gd.openGeoData()
    count = gpdf.shape[0] # Number of rows in the dataframe
    cid = random.randint(0, count)
    country = gpdf.iloc[cid]
    response = {'Country': country['name']}
    LOG.info("Getting a new question: " + str(response))
    return jsonify(response)

# Checks a user's answer. 
# Guess is the id of the country the user clicked on
# Country is the correct country.
@game_blueprint.route("/checkAnswer")
def checkAnswer():
    country = request.args.get('country', default='NONE', type = str)
    guess = request.args.get('guess', default = 0, type = int)
    gpdf = gd.openGeoData()

    LOG.info("Checking an answer Country: " + country + " Guess: " + str(guess))
    
    country_id = gd.lookupCountryID(country)

    LOG.debug("Inserting the guess into the databse")
    # Insert the guess into the database
    g = Guess(correctcountry=country_id, guesscountry=guess)
    db.session.add(Guess(correctcountry=country_id, guesscountry=guess))
    db.session.commit()
    LOG.debug("Insertion complete")

    if guess == country_id:
        response = {'Correct' : 'True'}
    else:
        guess_country = gpdf.iloc[guess]['name']
        distance = gd.calculateDistance(gpdf, country_id, guess)
        response = {'Correct' : 'False', 'CorrectID' : country_id, 'Guess' : guess_country, 'Distance' : int(distance)}
    return jsonify(response)