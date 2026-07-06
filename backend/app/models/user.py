from app.extensions import db

class User(db.Model):
    __tablename__="users"

    id = db.Column(db.Integer, primary_key=True)
    full_name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password_hash=db.Column(db.String(255), nullable=True)
    provider=db.Column(db.String(50),nullable=False, default="email")
    role=db.Column(db.String(50),nullable=False, default="user")
