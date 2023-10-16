from flask import Blueprint

bp = Blueprint('main', __name__)

from app.web import routes