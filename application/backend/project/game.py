from flask import Blueprint, jsonify, request
import project.geodata as gd
import random
import math
from project.config import LOG
from project import db
from project.guesses import Guess

game_blueprint = Blueprint('game', __name__)

@game_blueprint.route("/getQuestion")
def getQuestion():
    cdf = gd.openGeoData()
    count = cdf.shape[0] # Number of rows in the dataframe
    cid = random.randint(0, count)
    country = cdf.iloc[cid]
    response = {'Country': country['name']}
    LOG.info("Getting a new question: " + str(response))
    return jsonify(response)

@game_blueprint.route("/checkAnswer")
def checkAnswer():
    country = request.args.get('country', default='NONE', type = str)
    guess = request.args.get('guess', default = 0, type = int)
    cdf = gd.openGeoData()

    LOG.info("Checking an answer Country: " + country + " Guess: " + str(guess))
    
    c = cdf[cdf.name == country]
    country_id = int(c['id'])

    LOG.debug("Inserting the guess into the databse")
    # Insert the guess into the database
    g = Guess(correctcountry=country_id, guesscountry=guess)
    LOG.debug(g.to_json())
    db.session.add(Guess(correctcountry=country_id, guesscountry=guess))
    db.session.commit()
    LOG.debug("Insetion complete")

    if guess == country_id:
        LOG.debug("Guess was Correct Nice Job!")
        response = {'Correct' : 'True'}
    else:
        guess_country = cdf.iloc[guess]['name']
        LOG.debug("Guess was incorrect. :( Guessed Country: " + str(guess_country))
        distance = gd.calcDistance(cdf, country_id, guess)
        response = {'Correct' : 'False', 'CorrectID' : country_id, 'Guess' : guess_country, 'Distance' : int(distance)}
        LOG.debug(response)
    return jsonify(response)