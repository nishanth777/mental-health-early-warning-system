from flask import Blueprint


assessment_bp = Blueprint(
    "assessment",
    __name__,
    url_prefix="/assessment"
)

from . import routes 