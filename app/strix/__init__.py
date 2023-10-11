from flask import Blueprint

bp = Blueprint('strix', __name__)

from app.strix import routes