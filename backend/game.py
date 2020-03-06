from flask import Blueprint, jsonify, request
import geodata as gd
import random

gamer = Blueprint('game', __name__)

@gamer.route("/getQuestion")
def getQuestion():
    cdf = gd.openGeoData()
    count = cdf.shape[0] # Number of rows in the dataframe
    cid = random.randint(0, count)
    country = cdf.iloc[cid]
    response = {'Country': country['name']}
    return jsonify(response)

@gamer.route("/checkAnswer")
def checkAnswer():
    country = request.args.get('country', default='NONE', type = str)
    guess = request.args.get('guess', default = 0, type = int)
    cdf = gd.openGeoData()
    c = cdf[cdf.name == country]
    country_id = int(c['id'])
    if guess == country_id:
        response = {'Correct' : 'True'}
    else:
        guess_country = cdf.iloc[guess]['name']
        response = {'Correct' : 'False', 'CorrectID' : country_id, 'Guess' : guess_country}
    return jsonify(response)
