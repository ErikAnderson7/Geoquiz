from flask import Blueprint, jsonify, request, render_template, redirect
from project.geodata import getCountryList
from project.config import LOG

pages_blueprint = Blueprint('pages', __name__)

# Routes the user to the singleplayer game
@pages_blueprint.route("/")
def main_page():
    LOG.info("Opening single player game")
    return render_template("main.html")

# Routes the user to the statistics page
@pages_blueprint.route("/Statistics")
def statistics():
    LOG.info("Opening statistics page")
    countryList = getCountryList().sort_values() # Sorts the list of countries by name in alphabetical order
    return render_template("statistics.html", countryList=countryList)