from flask import Flask, jsonify, request, Blueprint
import project.geodata as gd
from project.config import LOG

maps_blueprint = Blueprint('maps', __name__) 

@maps_blueprint.route("/getWorld.json")
def getWorldMap():
	LOG.info("Getting the world map")
	countries_df = gd.getGameWorldMap()
	gjson = gd.gdfToGeoJSON(countries_df)
	return jsonify(gjson)

@maps_blueprint.route("/getCountry")
def getCountry():
	country = request.args.get('i', default=0, type = int)
	LOG.info("Getting country: " + str(country))
	cdf = gd.getGameWorldMap()
	return jsonify(gd.getCountry(cdf, country))
