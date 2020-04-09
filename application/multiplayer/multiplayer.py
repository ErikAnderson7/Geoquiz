from flask import Flask, Blueprint, jsonify, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from config import LOG
import json
import requests
from time import sleep
from games import addUser, getGame, addGuess, addNewQuestion, ColorTakenException, UsernameTakenException

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def test():
    return render_template("main.html")

@app.route("/maps/getWorld.json")
def get_world():
    LOG.info("Getting map from backend")
    mapGeoJSON = requests.get('http://server:5000/maps/getWorld.json').json()
    return jsonify(mapGeoJSON)

@app.route("/maps/getCountry")
def get_country():
    country = request.args.get('i', default=0, type = int)
    mapGeoJSON = requests.get(f'http://server:5000/maps/getCountry?i={country}').json()
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

@socketio.on('guess')
def check_answer(message):
    LOG.info("Message: " + str(message) + " Type: " +str(type(message)))
    country = message['country']
    guess = message['guess']
    username = message['username']
    room = message['room']

    check_url = f'http://server:5000/game/checkAnswer?country={country}&guess={guess}'
    response = requests.get(check_url).json()
    response['GuessID'] = guess
    response['country'] = country

    addGuess(room, username, response)
    game = getGame(room)
    emit('answer-response', game, broadcast=True, room=room)

    if(len(game['game']['users']) == len(game['game']['question']['guesses'])):
        LOG.info("Everyone has answered the question sending new question in 5 seconds")
        sleep(5)
        game = addNewQuestion(room)
        emit('new-question', game, broadcast=True, room=room)

@socketio.on('join')
def user_join_room(message):
    LOG.info("Message: " + str(message) + " Type: " +str(type(message)))
    username = message['username']
    room = message['room']
    color = message['color']
    try:
        addUser(room, username, color)
        join_room(room)
        LOG.info("User: " + str(username) + " has joined room: " + str(room))
        game = getGame(room)
        emit('joined', game, broadcast=True, room=room)
    except ColorTakenException as e:
        LOG.info("ColorTakeException: " + str(e))
        emit('join-error', str(e))
    except UsernameTakenException as e:
        LOG.info("UsernameTakenException: " + str(e))
        emit('join-error', str(e))