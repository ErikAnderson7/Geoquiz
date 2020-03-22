import datetime
from flask import current_app
from sqlalchemy.sql import func
from project import db

class Guess(db.Model):
    __tablename__ = 'guesses'
    
    guessid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correctcountry = db.Column(db.Integer)
    guesscountry = db.Column(db.Integer)

    def __init__(self, correctcountry, guesscountry):
        self.correctcountry = correctcountry
        self.guesscountry = guesscountry

    def to_json(self):
        return {
            'GuessID': self.guessid,
            'CorrectCountry': self.correctcountry,
            'GuessCountry': self.guesscountry
        }