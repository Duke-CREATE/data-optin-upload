from flask import Flask
import os
import dotenv

def create_app():
    app = Flask(__name__)

    from .routes import app_routes

    app.register_blueprint(app_routes)
    # Load environment variables
    dotenv.load_dotenv()
    app.secret_key = os.getenv('SECRET_KEY','')    

    return app
