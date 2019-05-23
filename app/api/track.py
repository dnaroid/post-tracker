from flask import g, request
from flask_restful import Resource

from app import auth, db
from app.helpers.react_helper import as_json
from app.models import Track


class TracksAPI(Resource):
    decorators = [auth.login_required]

    def get(self):
        tracks = g.user.tracks.all()
        return {'data': as_json(tracks)}, 200


class TrackAPI(Resource):
    decorators = [auth.login_required]

    def get(self, number):
        track = Track.query.filter_by(number=number).first()
        if track is None:
            return {'error': 'not found'}, 404
        return as_json(track), 200


class TrackNewAPI(Resource):
    decorators = [auth.login_required]

    def post(self):
        data = request.get_json(force=True)
        if not data:
            return {'message': 'No input data provided'}, 400
        track = Track(
            user_id=g.user.id,
            number=data['number'],
            title=data['title']
        )
        db.session.add(track)
        db.session.commit()

        return as_json(track), 200
