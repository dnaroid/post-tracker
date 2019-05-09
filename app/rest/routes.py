from flask import jsonify, make_response, request
from flask_login import current_user, login_required

from app import db
from app.helpers.react_helper import as_json
from app.main import bp
from app.models import Track, User


# guide https://realpython.com/token-based-authentication-with-flask/


@bp.route('/rest/auth/register', methods=['POST'])
def register():
    post_data = request.get_json()
    user = User.query.filter_by(email=post_data.get('email')).first()
    if not user:
        try:
            user = User(
                email=post_data.get('email'),
                password=post_data.get('password')
            )
            db.session.add(user)
            db.session.commit()
            auth_token = user.encode_auth_token(user.id)
            responseObject = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
            }
            return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return make_response(jsonify(responseObject)), 202


@bp.route('/rest/tracks', methods=['GET'])
@login_required
def rest_tracks():
    tracks = current_user.tracks.all()
    return as_json(tracks)


@bp.route('/rest/track/<number>', methods=['GET'])
@login_required
def rest_track(number):
    track = Track.query.filter_by(number=number).first_or_404()
    return as_json(track)
