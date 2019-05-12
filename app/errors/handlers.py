from flask import jsonify, make_response

from app import db
from app.errors import bp


@bp.app_errorhandler(401)
def need_auth_error(error):
    return make_response(jsonify({'error': 'need auth'})), 401


@bp.app_errorhandler(404)
def not_found_error(error):
    return make_response(jsonify({'error': 'not found'})), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return make_response(jsonify({'error': 'server error'})), 500
