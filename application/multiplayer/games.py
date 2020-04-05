from config import LOG, db
import json
import requests

def getGame(room):
    g = db.games.find({ 'room': room })
    LOG.info(g)
    LOG.info(g.count())
    LOG.info(g.collection)
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

def addUser(room, username):
    LOG.info("Adding user: " + username + " to room: " + room)
    game = getGame(room)
    game['game']['users'][username] = {
        'totalGuesses': 0,
        'correctGuesses': 0,
        'averageDistance': 0
    }
    updateGame(room, game)

def addGuess(room, username, guess):
    LOG.info("ADDING A GUESS")
