from flask import jsonify, request
from app.models.user import User
from app.extensions import bcrypt,db
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
    ),200

   