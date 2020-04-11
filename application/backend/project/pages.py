from flask import Blueprint, jsonify, request, render_template, redirect

pages_blueprint = Blueprint('pages', __name__)

@pages_blueprint.route("/")
def main_page():
    return render_template("main.html")

@pages_blueprint.route("/Multiplayer")
def multiplayer():
    return redirect("https://multiplayer.geoquiz.io/")

@pages_blueprint.route("/Statistics")
def statistics():
    return render_template("comingsoon.html")

@pages_blueprint.route("/Singleplayer")
def singleplayer():
    return redirect("/")

if __name__ == '__main__':
	app.run()