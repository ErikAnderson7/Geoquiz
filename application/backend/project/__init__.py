import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate


# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from project.pages import pages_blueprint
    app.register_blueprint(pages_blueprint, url_prefix='/')

    from project.maps import maps_blueprint
    app.register_blueprint(maps_blueprint, url_prefix='/maps')

    from project.game import game_blueprint
    app.register_blueprint(game_blueprint, url_prefix='/game')

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app