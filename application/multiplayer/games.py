from config import LOG, db
import json
import requests

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

def getGame(room):
    g = db.games.find({'room': room})
    try:
        game = g[0]
        LOG.info(game)
    except IndexError as e:
        LOG.info("Game: " + room + " Does not yet exist, creating new game")
        question = requests.get('http://server:5000/game/getQuestion').json()
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
    del game['_id']
    return game

def updateGame(room, game):
    LOG.info("Updating Game: " + str(room))
    LOG.info(game)
    db.games.update({'room': room}, game)

def addUser(room, username, color):
    LOG.info("Adding user: " + username + " to room: " + room)
    game = getGame(room)
    if username in game['game']['users'].keys():
        raise UsernameTakenException("Username is already taken.")
    for user in game['game']['users']:
        LOG.info(user)
        if game['game']['users'][user]['color'] == color:
            raise ColorTakenException("Another user already has choosen " + color)
    game['game']['users'][username] = {
        'color': color,
        'totalGuesses': 0,
        'correctGuesses': 0,
        'averageDistance': 0,
        'totalDistance': 0
    }
    updateGame(room, game)

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

def addNewQuestion(room):
    game = getGame(room)
    question = requests.get('http://server:5000/game/getQuestion').json()
    game['game']['question']['guesses'] = {}
    game['game']['question']['Country'] = question['Country']
    updateGame(room, game)
    return game
