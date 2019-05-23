from flask import Blueprint
from flask_restful import Api

from app.api.auth import LoginAPI, LogoutAPI, RegisterAPI, StatusAPI
from app.api.track import TrackAPI, TracksAPI, TrackNewAPI

bp = Blueprint('api', __name__)
api = Api(bp)

api.add_resource(TracksAPI, '/tracks')
api.add_resource(TrackAPI, '/track/<string:id>')
api.add_resource(TrackNewAPI, '/track')

api.add_resource(RegisterAPI, '/register')
api.add_resource(LoginAPI, '/login')
api.add_resource(LogoutAPI, '/logout')
api.add_resource(StatusAPI, '/status')
