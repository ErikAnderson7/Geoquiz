from flask import Flask, Blueprint, jsonify, request, render_template
from flask_socketio import SocketIO, emit
from config import LOG
import json
import requests
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.logging = False

@app.route("/")
def test():
    LOG.info("Hostname: " + str(socket.gethostname()))
    return render_template("main.html")

@app.route("/maps/getWorld.json")
def get_world():
    LOG.info("Getting map from backend")
    mapGeoJSON = requests.get('http://server:5000/maps/getWorld.json').json()
    return jsonify(mapGeoJSON)

@app.route("/maps/getCountry")
def get_country():
    country = request.args.get('i', default=0, type = int)
    mapGeoJSON = requests.get('http://server:5000/maps/getCountry?i={country}').json()
    return jsonify(mapGeoJSON)

@socketio.on('message')
def handle_message(message):
    LOG.info('received message: ' + message)
    
@socketio.on('connected')
def send_message(message):
    LOG.info(message)
    emit('message', 'You are connected!')

@socketio.on('get-question')
def get_question(message):
    LOG.info(message)
    question = requests.get('http://server:5000/game/getQuestion').json()
    LOG.info(question)
    emit('question', question)

@socketio.on('check-answer')
def check_answer(message):
    LOG.info(message)
    country = message['country']
    guess = message['guess']
    check_url = 'http://server:5000/game/checkAnswer?country={}&guess={}'.format(country, guess)
    response = requests.get(check_url).json()
    # Return back the answer information to the client. 
    # In single player (HTTP) They already have this information in the checkAnswer method.
    # Because of the way Websockets work they dont have this info, so give it back to them.
    response['GuessID'] = guess
    response['country'] = country
    emit('answer-response', response)