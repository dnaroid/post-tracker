from flask import g
from flask_restful import Resource

from app import auth
from app.helpers.react_helper import as_json
from app.models import Track


class TracksAPI(Resource):
    decorators = [auth.login_required]

    def get(self):
        tracks = g.user.tracks.all()
        return as_json(tracks), 200


class TrackAPI(Resource):
    decorators = [auth.login_required]

    def get(self, number):
        track = Track.query.filter_by(number=number).first()
        if track is None:
            return {'error': 'not found'}, 404
        return as_json(track), 200

    # def post(self):
    #     json_data = request.get_json(force=True)
    #     if not json_data:
    #         return {'message': 'No input data provided'}, 400
    #     # Validate and deserialize input
    #     data, errors = comment_schema.load(json_data)
    #     if errors:
    #         return {"status": "error", "data": errors}, 422
    #     category_id = Category.query.filter_by(id=data['category_id']).first()
    #     if not category_id:
    #         return {'status': 'error', 'message': 'comment category not found'}, 400
    #     comment = Comment(
    #         category_id=data['category_id'],
    #         comment=data['comment']
    #     )
    #     db.session.add(comment)
    #     db.session.commit()
    #
    #     result = comment_schema.dump(comment).data
    #
    #     return {'status': "success", 'data': result}, 201
