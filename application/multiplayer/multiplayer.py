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

@app.route("/")
def multiplayer():
    return render_template("multiplayer.html")

# Gets the map of the world from the normal backend
@app.route("/maps/getWorld.json")
def get_world():
    LOG.info("Getting map from Geoquiz")
    mapGeoJSON = requests.get('http://geoquiz:5000/maps/getWorld.json').json()
    return jsonify(mapGeoJSON)

# Gets a country GeoJSON data from the normal backend
@app.route("/maps/getCountry")
def get_country():
    country = request.args.get('i', default=0, type = int)
    mapGeoJSON = requests.get(f'http://geoquiz:5000/maps/getCountry?i={country}').json()
    return jsonify(mapGeoJSON)

@app.route("/Multiplayer")
def redirect_multiplayer():
    LOG.info("Redirecting user to multiplayer")
    return redirect("/")

# Handles when a user submits a guess
@socketio.on('guess')
def check_answer(message):
    LOG.info("Message: " + str(message) + " Type: " +str(type(message)))
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
        game = addNewQuestion(room)
        emit('new-question', game, broadcast=True, room=room)

# Handles when a user is trying to join a game
# Emits join-error event if they are trying to use an already taken username or color
# If joining game was successful it broadcasts to every user in the game
@socketio.on('join')
def user_join_room(message):
    LOG.info("Message: " + str(message) + " Type: " +str(type(message)))
    username = message['username']
    room = message['room']
    color = message['color']
    try:
        addUser(room, username, color, request.sid)
        join_room(room)
        LOG.info("User: " + str(username) + " has joined room: " + str(room))
        game = getGame(room)
        emit('joined', game, broadcast=True, room=room)
    except ColorTakenException as e:
        emit('join-error', str(e))
    except UsernameTakenException as e:
        emit('join-error', str(e))

# Handles when a user disconnects from the websocket server
# Removes the user from the game they were in
@socketio.on('disconnect')
def disconnect_user():
    LOG.info("User: " + str(request.sid) + " has disconnected")
    game = removeUser(request.sid)
    if(game != None):
        emit('user-disconnected', game, broadcast=True, room=game['room'])
