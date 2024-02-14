from flask import Flask
import os


def create_app():
    app = Flask(__name__)

    from .routes import app_routes

    app.register_blueprint(app_routes)
    app.secret_key = os.getenv('SECRET_KEY','')    

    return app
