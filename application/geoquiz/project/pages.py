from flask import Blueprint, jsonify, request, render_template, redirect
from project.geodata import getCountryList
from project.config import LOG

pages_blueprint = Blueprint('pages', __name__)

@pages_blueprint.route("/")
def main_page():
    return render_template("main.html")

@pages_blueprint.route("/Statistics")
def statistics():
    countryList = getCountryList().sort_values()
    LOG.info(str(type(countryList)))
    return render_template("statistics.html", countryList=countryList)

@pages_blueprint.route("/Singleplayer")
def singleplayer():
    return redirect("/")

if __name__ == '__main__':
	app.run()