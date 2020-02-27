from flask import Flask, render_template, jsonify, Markup, request
import geodata as gd

app = Flask(__name__) 

@app.route("/")
def test():
	return render_template('main.html')

@app.route("/getWorld.json")
def getWorldMap():
	countries_df = gd.getGameWorldMap()
	gjson = gd.gdfToGeoJSON(countries_df)
	return jsonify(gjson)

@app.route("/getCountry")
def getCountry():
	country = request.args.get('i', default=0, type = int)
	print("Getting country: " + str(country))
	cdf = gd.getGameWorldMap()
	return jsonify(gd.getCountry(cdf, country))


from game import gamer
app.register_blueprint(gamer, url_prefix='/game')