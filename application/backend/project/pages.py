from flask import Blueprint, jsonify, request, render_template

pages_blueprint = Blueprint('pages', __name__)

@pages_blueprint.route("/")
def main_page():
    return render_template("main.html")

@pages_blueprint.route("/Multiplayer")
def multiplayer():
    return render_template("comingsoon.html")

@pages_blueprint.route("/Statistics")
def statistics():
    return render_template("comingsoon.html")

@pages_blueprint.route("/Singleplayer")
def singleplayer():
    return render_template("main.html")

if __name__ == '__main__':
	app.run()