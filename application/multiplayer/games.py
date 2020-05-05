from config import LOG, gameDB, userDB
import json
import requests

# ColorTakenException occurs when a user tries to join a room with a color another user has already chosen
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

# UserNameTakenException occurs when a user tries to join a room with a username another user has already chosen
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
    g = gameDB.games.find({'room': room})
    try:
        game = g[0]
    except IndexError as e:
        LOG.info("Game: " + room + " Does not yet exist, creating new game")
        game = createGame(room)

    del game['_id'] # Remove the object id as it is not JSON serializable

    return game

# Creates a new game with given room name
def createGame(room):
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
    gameDB.games.insert(game)
    
    return game

# Updates the game in mongodb
def updateGame(room, game):
    LOG.info("Updating Game: " + str(room))
    gameDB.games.update({'room': room}, game)

# Adds a user to a multiplayer game and the user db
# Throws exections if the choosen username or color is already taken
def addUser(room, username, color, sid):
    LOG.info("Adding user: " + username + " to room: " + room)
    
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
    userDB.users.insert(user)

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

# Removes a user from the game they were in
# Finds the user in the user db and removes them from the game they were in and the user db
def removeUser(sid):
    user = userDB.users.find({'sid': sid})[0]
    room = user['room']
    game = getGame(room)

    # Remove the user from the game and the user db
    del(game['game']['users'][user['username']])
    userDB.users.delete_one({'sid': sid})

    # If the game no longer has any users delete the game from the game db and return None
    if(len(game['game']['users']) == 0):
        gameDB.games.delete_one({'room': room})
        return None
    else:
        updateGame(room, game)
        return game
