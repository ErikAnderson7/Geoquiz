from flask import Flask, render_template, jsonify, Markup
import geodata as gd

app = Flask(__name__) 

@app.route("/")
def test():
	cdf = gd.openSHPFile()
	t = testModel(gd.getSVG(cdf))
	return render_template('main.html')

@app.route("/getWorld.json")
def getWorldMap():
	countries_df = gd.openSHPFile()
	gjson = gd.gdfToGeoJSON(countries_df)
	return jsonify(gjson)
