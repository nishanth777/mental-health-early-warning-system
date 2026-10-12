import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Prefer the managed database URL in production.
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Render PostgreSQL URLs may use the "postgres://" scheme.
        # SQLAlchemy expects "postgresql://" or a driver-specific scheme.
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1,
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:
        # Local development: use individual database variables.
        SQLALCHEMY_DATABASE_URI = URL.create(
            drivername="postgresql+psycopg2",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False