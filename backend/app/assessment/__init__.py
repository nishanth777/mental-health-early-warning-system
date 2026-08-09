from flask import Blueprint

print(">>> Loading assessment blueprint")

assessment_bp = Blueprint(
    "assessment",
    __name__,
    url_prefix="/assessment"
)

print(">>> Importing assessment routes")
from . import routes
print(">>> Assessment routes imported")