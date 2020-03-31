import os

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)
    socketio = SocketIO(app)

    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    socketio.init_app(app)
    socketio.logger = True

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'socketio': socketio}

    return app