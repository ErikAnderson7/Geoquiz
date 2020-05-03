from flask import Blueprint, jsonify, request
import project.geodata as gd
import pandas
import geopandas
import numpy as np
import math
from sqlalchemy import func, asc
from project.config import LOG
from project import db
from project.guesses import Guess
import project.stats as stats

stats_blueprint = Blueprint('stats', __name__)

# Gets the map containing stats for a given country
@stats_blueprint.route("/perCountryMap")
def perCountryMap():
    country = request.args.get('country', default=0, type = str)
    LOG.info("Getting " + country + "'s stats map")
    
    country_id = gd.lookupCountryID(country)
    countryMap = stats.getPerCountryMap(country_id)

    return jsonify(countryMap)

# Gets the general stats for a given country
@stats_blueprint.route("/perCountry")
def perCountryStats():
    country = request.args.get('country', default=0, type = str)
    countryid = gd.lookupCountryID(country)
    LOG.info("Getting " + country + "'s stats")
    countryStats = stats.getPerCountryStats(countryid)

    return jsonify(countryStats)

# Gets the map containing general stats for each country
@stats_blueprint.route("/globalMap")
def globalMap():
    LOG.info("Getting global stats map")
    globalStatsMap = stats.getGlobalStatsMap()

    return jsonify(globalStatsMap)

# Gets the general stats for the entire world
@stats_blueprint.route("/global")
def globalStats():
    LOG.info("Getting global stats")
    gStats = stats.getGlobalStats()

    return jsonify(gStats)

