from datetime import datetime
from hashlib import md5

import redis
import rq
from flask import current_app
from flask_login import UserMixin
from itsdangerous import (BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer)

from app import bcrypt, db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    tracks = db.relationship('Track', backref='owner', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt \
            .generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')) \
            .decode()
        self.registered_on = datetime.now()

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    # def get_reset_password_token(self, expires_in=600):
    #     return jwt.encode(
    #         {'reset_password': self.id, 'exp': time() + expires_in},
    #         current_app.config['SECRET_KEY'],
    #         algorithm='HS256').decode('utf-8')
    #
    # @staticmethod
    # def verify_reset_password_token(token):
    #     try:
    #         id = jwt.decode(token, current_app.config['SECRET_KEY'],
    #                         algorithms=['HS256'])['reset_password']
    #     except:
    #         return
    #     return User.query.get(id)

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def generate_auth_token(self, expiration=6000):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def get_by_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(30), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(200))
    events = db.relationship('Event', backref='track', lazy='dynamic')
    is_archived = db.Column(db.Integer, default=0)

    def serialize(self):
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'image_url': self.image_url,
        }


class Event(db.Model):
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    title = db.Column(db.String(200))

    def __repr__(self):
        return f'<Event {self.timestamp} {self.title} >'


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
