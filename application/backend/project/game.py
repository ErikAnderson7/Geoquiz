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
    return jsonify(response)

@game_blueprint.route("/checkAnswer")
def checkAnswer():
    country = request.args.get('country', default='NONE', type = str)
    guess = request.args.get('guess', default = 0, type = int)
    cdf = gd.openGeoData()
    
    c = cdf[cdf.name == country]
    country_id = int(c['id'])

    # Insert the guess into the database
    g = Guess(correctcountry=country_id, guesscountry=guess)
    LOG.info(g.to_json())
    db.session.add(Guess(correctcountry=country_id, guesscountry=guess))
    db.session.commit()

    if guess == country_id:
        response = {'Correct' : 'True'}
    else:
        guess_country = cdf.iloc[guess]['name']
        distance = calcDistance(cdf, country_id, guess)
        response = {'Correct' : 'False', 'CorrectID' : country_id, 'Guess' : guess_country, 'Distance' : int(distance)}
    return jsonify(response)

# Calculates the distance between two countries with the haversine method
def calcDistance(cdf, country1_id, country2_id):
    import math

    c1 = cdf.iloc[country1_id]
    country1Coords = [c1['geometry'].centroid.x, c1['geometry'].centroid.y]

    c2 = cdf.iloc[country2_id]
    country2Coords = [c2['geometry'].centroid.x, c2['geometry'].centroid.y]

    lon1, lat1 = country1Coords
    lon2, lat2 = country2Coords
    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters
    km = meters / 1000.0  # output distance in kilometers

    meters = round(meters)
    km = round(km, 3)
    return km