from flask import Blueprint

bp = Blueprint('rest', __name__)

from app.rest import routes
