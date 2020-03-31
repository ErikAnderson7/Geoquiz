from flask import Flask, Blueprint, jsonify, request, render_template
from flask_socketio import SocketIO
from config import LOG

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def test():
    return render_template("multiplayer-start.html")

@socketio.on('message')
def handle_message(message):
    LOG.info('received message: ' + message)

if __name__ == '__main__':
    socketio.run(app)