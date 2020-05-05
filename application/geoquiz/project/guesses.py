import datetime
from flask import current_app
from sqlalchemy.sql import func
from project import db

# Model used to store guesses
class Guess(db.Model):
    __tablename__ = 'guesses'
    
    guessid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correctcountry = db.Column(db.Integer) # country id of the country that the user was prompted to guess
    guesscountry = db.Column(db.Integer) # country id of the country that user guessed

    def __init__(self, correctcountry, guesscountry):
        self.correctcountry = correctcountry
        self.guesscountry = guesscountry