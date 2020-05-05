from flask import Flask, Blueprint, jsonify, request, render_template, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from config import LOG
import json
import requests
from time import sleep
from games import addUser, getGame, addGuess, addNewQuestion, ColorTakenException, UsernameTakenException, removeUser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins=['http://multiplayer.geoquiz.io', 'http://localhost:5002'])

# Routes the user to the multiplayer game
@app.route("/")
def multiplayer():
    return render_template("multiplayer.html")

# Gets the map of the world from the normal backend
@app.route("/game/getGameMap")
def getGameWorld():
    LOG.info("Getting map from Geoquiz")
    mapGeoJSON = requests.get('http://geoquiz:5000/game/getGameMap').json()
    return jsonify(mapGeoJSON)

# Gets a country GeoJSON data from the normal backend
@app.route("/game/getCountryMap")
def getCountry():
    country = request.args.get('i', default=0, type = int)
    mapGeoJSON = requests.get(f'http://geoquiz:5000/game/getCountryMap?i={country}').json()
    return jsonify(mapGeoJSON)

# Handles when a user submits a guess
@socketio.on('guess')
def checkAnswer(message):
    LOG.info("User has submitted their guess. Message: " + str(message))
    country = message['country']
    guess = message['guess']
    username = message['username']
    room = message['room']

    # Check the user's guess by checking with the singleplayer backend
    check_url = f'http://geoquiz:5000/game/checkAnswer?country={country}&guess={guess}'
    response = requests.get(check_url).json()
    response['GuessID'] = guess
    response['country'] = country

    addGuess(room, username, response)
    game = getGame(room)
    emit('answer-response', game, broadcast=True, room=room)

    # If everyone has answered the question, wait 5 seconds and get a new question
    if(len(game['game']['users']) == len(game['game']['question']['guesses'])):
        LOG.info("Everyone has answered the question sending new question in 5 seconds")
        sleep(5)
        addNewQuestion(room)
        game = getGame(room)
        emit('new-question', game, broadcast=True, room=room)

# Handles when a user is trying to join a game
# Emits join-error event if they are trying to use an already taken username or color
# If joining game was successful it broadcasts to every user in the game
@socketio.on('join')
def userJoiningRoom(message):
    LOG.info("User is attemping to join a game. Message: " + str(message))
    username = message['username']
    room = message['room']
    color = message['color']

    # Try to add the user to the multiplayer game
    try:
        addUser(room, username, color, request.sid)
        join_room(room)
        LOG.info("User: " + str(username) + " has joined room: " + str(room))
        game = getGame(room)
        emit('joined', game, broadcast=True, room=room)
    except ColorTakenException as e: # Username already taken
        emit('join-error', str(e))
    except UsernameTakenException as e: # Color already taken
        emit('join-error', str(e))

# Handles when a user disconnects from the websocket server
# Removes the user from the game they were in
@socketio.on('disconnect')
def userDisconnected():
    LOG.info("User: " + str(request.sid) + " has disconnected")
    game = removeUser(request.sid)
    if(game != None): # If the game still exists tell other users that another user has disconnected.
        LOG.info("Sending updated game state to remaining users")
        emit('user-disconnected', game, broadcast=True, room=game['room'])
