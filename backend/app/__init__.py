from flask import Flask
from flask_cors import CORS

from config import Config
from app.extensions import db, bcrypt, jwt, migrate

# Import models
from app.models.user import User
from app.models.assessment import Assessment

# Import blueprints
from app.auth import auth_bp
from app.assessment import assessment_bp
from app.dashboard import dashboard_bp


def create_app():
    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(Config)

    # Enable CORS for local development and the deployed frontend
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:5173",
                    "https://mental-health-early-warning-system.vercel.app",
                ]
            }
        },
        supports_credentials=True,
        allow_headers=[
            "Content-Type",
            "Authorization",
        ],
        methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],
    )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(
        auth_bp,
        url_prefix="/auth",
    )

    app.register_blueprint(
        assessment_bp,
        url_prefix="/assessment",
    )

    app.register_blueprint(
        dashboard_bp,
        url_prefix="/dashboard",
    )

    @app.route("/")
    def home():
        return {
            "message": "Mental Health Early Warning System API",
            "status": "running",
        }

    return app