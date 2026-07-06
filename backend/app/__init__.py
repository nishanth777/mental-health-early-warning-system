from flask import Flask

from config import Config
from app.extensions import db, bcrypt, jwt, migrate
from app.models.user import User

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def home():
        return {
            "message": "Mental Health Early Warning System API",
            "status": "running",
        }

    return app