from flask import Flask

from config import Config
from app.extensions import db, bcrypt, jwt, migrate
from app.models.user import User
from app.models.assessment import Assessment
from app.auth import auth_bp
def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    @app.route("/")
    def home():
        return {
            "message": "Mental Health Early Warning System API",
            "status": "running",
        }

    return app