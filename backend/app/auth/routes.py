from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.models.user import User
from app.extensions import bcrypt, db
from . import auth_bp


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify(
            {
                "error": "All fields are required"
            }
        ), 400
    
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify(
            {
                "error":"Email already registered"
            }
        ),409
    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(
    full_name=full_name,
    email=email,
    password_hash=hashed_password
)
    db.session.add(user)
    db.session.commit()
    
    
    
    return jsonify(
        {
            "message": "User registered successfully"
        }
    ),201



@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify(
            {
                "error":"Email or Password are required"
            }
        ),400
    
    user=User.query.filter_by(email=email).first()
    if not user:
        return jsonify(
        {
            "error": "Invalid email or password"
        }
    ), 401

    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify(
            {
                "error":"Invalid email or password"
            }
        ),401
    
    access_token=create_access_token(identity=str(user.id))
    
    return jsonify(
        {
           "message": "Login successful",
            "access_token": access_token  
        }
    ), 200

@auth_bp.route("/google", methods=["POST"])
def google_login():
    data = request.get_json()

    google_token = data.get("credential")

    if not google_token:
        return jsonify(
            {
                "error": "Google credential is required"
            }
        ), 400

    try:
        GOOGLE_CLIENT_ID = "101681046390-bg14ds2o6kmu0snob1prfisnprrgh000.apps.googleusercontent.com"

        idinfo = id_token.verify_oauth2_token(
            google_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        full_name = idinfo.get("name")

        if not email:
            return jsonify(
                {
                    "error": "Google account email not available"
                }
            ), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                full_name=full_name or "Google User",
                email=email,
                password_hash=None,
                provider="google"
            )

            db.session.add(user)
            db.session.commit()

        access_token = create_access_token(
            identity=str(user.id)
        )

        return jsonify(
            {
                "message": "Google login successful",
                "access_token": access_token
            }
        ), 200

    except ValueError:
        return jsonify(
            {
                "error": "Invalid Google credential"
            }
        ), 401

    

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    

    identity = get_jwt_identity()

    user = User.query.filter_by(id=identity).first()

    if not user:
        return jsonify(
            {
                "error": "User not found"
            }
        ), 404

    return jsonify(
        {
            "full_name": user.full_name,
            "email": user.email
        }
    ), 200