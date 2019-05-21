from flask import g, request
from flask_restful import Resource

from app import auth, bcrypt, db
from app.helpers.auth_helper import get_token
from app.models import User


@auth.verify_password
def verify_password(username_or_token, password):
    if request.method != 'OPTIONS':
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
                user = User.get_by_token(auth_token)
                if user is None:
                    return False
                g.user = user
            except IndexError:
                return False
    return True


class RegisterAPI(Resource):
    def post(self):
        post_data = request.get_json()
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    email=post_data.get('email'),
                    password=post_data.get('password'))
                db.session.add(user)
                db.session.commit()
                auth_token = user.generate_auth_token()
                return {'status': 'success',
                        'message': 'Successfully registered.',
                        'token': auth_token.decode()}, 201
            except Exception as e:
                return {'status': 'fail',
                        'message': 'Some error occurred. Please try again.'}, 401
        else:
            return {'status': 'fail',
                    'message': 'User already exists. Please Log in.'}, 202


class LoginAPI(Resource):
    def post(self):
        post_data = request.get_json()
        try:
            user = User.query.filter_by(email=post_data.get('email')).first()
            if user and bcrypt.check_password_hash(user.password, post_data.get('password')):
                auth_token = user.generate_auth_token()
                return {'status': 'success',
                        'message': 'Successfully logged in.',
                        'token': auth_token.decode()}, 200
            else:
                return {'status': 'fail',
                        'message': 'User does not exist.'}, 404
        except Exception as e:
            return {'status': 'fail',
                    'message': 'Try again'}, 500


class LogoutAPI(Resource):
    def post(self):
        # insert the token
        # db.session.add(blacklist_token)
        # db.session.commit()
        auth_token = get_token()
        if auth_token:
            user = User.get_by_token(auth_token)
            if not user:
                return {'status': 'fail',
                        'data': {
                            'message': 'Invalid auth token.'}}, 401
            else:
                return {'status': 'success',
                        'data': {
                            'user_id': user.id,
                            'email': user.email}}, 200


class StatusAPI(Resource):
    def get(self):
        auth_token = get_token()
        if auth_token:
            user = User.get_by_token(auth_token)
            if not user:
                return {'status': 'fail',
                        'data': {
                            'message': 'Invalid auth token.'}}, 401
            else:
                return {'status': 'success',
                        'data': {
                            'user_id': user.id,
                            'email': user.email}}, 200
        else:
            return {'status': 'fail',
                    'data': {
                        'message': 'Invalid auth token.'}}, 401
