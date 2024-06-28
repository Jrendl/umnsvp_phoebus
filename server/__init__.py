"""
@package docstring
Application Factory for the flask server
"""

import os
import sys
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()

socketio = SocketIO()


def create_app(test_config=None):
    """Application factory function
        Initializes the App
        @param test_config path to a config file
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
    app.config['SECRET_KEY'] = 'dev'
    # initialize the app for the database
    db.init_app(app)
    CORS(app)

    # handle if a config was passed in
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register telemetry blueprint
    from . import telemetry
    app.register_blueprint(telemetry.bp)

    # register global variable blueprint
    from . import globals
    app.register_blueprint(globals.bp)

    # create database based upon SQLAlchemy model
    from . import model
    with app.app_context():
        db.create_all()

    socketio.init_app(app, cors_allowed_origins="*")
    return app
