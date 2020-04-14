from flask_socketio import emit
from config import LOG, db, user_db
import json
import requests
import threading
import time

timers = {}

class GameTimer(threading.Thread):
    def __init__(self, room, round_time):
        threading.Thread.__init__(self)
        self.room = room
        self.round_time = round_time
    def run(self):
        LOG.info("Starting timer for Game: " + self.room)
        while(True):
            time.sleep(self.round_time) # Sleep 30 seconds
            LOG.info("Sending new question to Game: " + self.room)
            game = addNewQuestion(self.room)
            emit('new-question', game, broadcast=True, room=self.room)

def createTimer(room, round_time):
    LOG.info("Adding a new timer for Game" + room)
    timer = GameTimer(room, round_time)
    timers[room] = timer
    timer.start()
    LOG.info(timers)

def stopTimer(room):
    LOG.info("Removing timer for Game: " + room)
    del(timers[room])
    LOG.info(timers)

class ColorTakenException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
    def __str__(self):
        if self.message:
            return self.message
        else:
            return "ColorTakenException raised"

class UsernameTakenException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
    def __str__(self):
        if self.message:
            return self.message
        else:
            return "UsernameTakenException raised"

# Gets a game with matching room
# If the game does not exist it creates the game
def getGame(room):
    room = room.replace(" ", "").lower() # Remove whitespace and convert to lower case
    g = db.games.find({'room': room})
    try:
        game = g[0]
        LOG.info(game)
    except IndexError as e:
        LOG.info("Game: " + room + " Does not yet exist, creating new game")
        question = requests.get('http://geoquiz:5000/game/getQuestion').json()
        game = {'room': room, 
                'game': {
                            'question': {
                                'Country': question['Country'],
                                'guesses': {}
                            }, 
                            'users': {}
                        }
                }
        db.games.insert(game)
        createTimer(room, 30)
    del game['_id']
    return game

# Updates the game in mongodb
def updateGame(room, game):
    room = room.replace(" ", "").lower() # Remove whitespace and convert to lower case
    LOG.info("Updating Game: " + str(room))
    LOG.info(game)
    db.games.update({'room': room}, game)

# Adds a user to a multiplayer game and the user db
# Throws exections if the choosen username or color is already taken
def addUser(room, username, color, sid):
    LOG.info("Adding user: " + username + " to room: " + room)
    room = room.replace(" ", "").lower() # Remove whitespace and convert to lower case
    
    game = getGame(room)
    if username in game['game']['users'].keys():
        raise UsernameTakenException("Username is already taken.")
    for user in game['game']['users']:
        if game['game']['users'][user]['color'] == color:
            raise ColorTakenException("Another user already has choosen " + color)
    
    user = {
        'sid': sid,
        'room': room,
        'username': username
    }
    LOG.info("Added new user " + str(user))
    user_db.users.insert(user)

    game['game']['users'][username] = {
        'color': color,
        'totalGuesses': 0,
        'correctGuesses': 0,
        'averageDistance': 0,
        'totalDistance': 0
    }
    updateGame(room, game)

# Adds a user's guess to the game
# Also updates the user's score
def addGuess(room, username, guess):
    LOG.info("User: " + username + " Room: " + room + " Guess: " + str(guess))
    
    game = getGame(room)
    game['game']['question']['guesses'][username] = guess
    prevScore = game['game']['users'][username]

    if(guess['Correct'] == 'True'):
        game['game']['users'][username]['totalGuesses'] = prevScore['totalGuesses'] + 1
        game['game']['users'][username]['correctGuesses'] = prevScore['correctGuesses'] + 1
        game['game']['users'][username]['averageDistance'] = prevScore['totalDistance'] / game['game']['users'][username]['totalGuesses']
    else:
        game['game']['users'][username]['totalGuesses'] = prevScore['totalGuesses'] + 1
        game['game']['users'][username]['totalDistance'] = prevScore['totalDistance'] + guess['Distance'] 
        game['game']['users'][username]['averageDistance'] = game['game']['users'][username]['totalDistance'] / game['game']['users'][username]['totalGuesses']

    updateGame(room, game)

# Updates the current question of a game
def addNewQuestion(room):
    game = getGame(room)
    question = requests.get('http://geoquiz:5000/game/getQuestion').json()
    game['game']['question']['guesses'] = {}
    game['game']['question']['Country'] = question['Country']
    updateGame(room, game)

    return game

# Removes a user from the game they were in
# Finds the user in the user db and removes them from the game they were in and the user db
def removeUser(sid):
    user = user_db.users.find({'sid': sid})[0]
    room = user['room']
    game = getGame(room)

    del(game['game']['users'][user['username']])
    user_db.users.delete_one({'sid': sid})

    if(len(game['game']['users']) == 0):
        db.games.delete_one({'room': room})
        stopTimer(room)
        return None
    else:
        updateGame(room, game)
        return game
