from flask import Flask, jsonify, request, Blueprint
import project.geodata as gd
from project.config import LOG

maps_blueprint = Blueprint('maps', __name__) 

# Returns the GeoJSON data for the entire world
@maps_blueprint.route("/getWorld.json")
def getWorldMap():
	LOG.info("Getting the world map")
	countries_df = gd.getGameWorldData()
	return jsonify(countries_df.to_json())

# Returns the GeoJSON data for a specific country
@maps_blueprint.route("/getCountry")
def getCountry():
	country = request.args.get('i', default=0, type = int)
	LOG.info("Getting country: " + str(country))
	return jsonify(gd.getCountry(country).to_json())
