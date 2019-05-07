import json
import sys
import time

from flask import render_template
from rq import get_current_job

from app import create_app, db
from app.email import send_email
from app.models import User, Track, Task

app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_tasks(user_id):
    try:
        user = User.query.get(user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_tracks = user.tracks.count()
        for track in user.tracks.order_by(Track.timestamp.asc()):
            data.append({'number': track.number, 'title': track.title,
                         'timestamp': track.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_tracks)

        send_email('[Tracker] Your blog posts',
                   sender=app.config['ADMIN'], recipients=[user.email],
                   text_body=render_template('email/export_posts.txt', user=user),
                   html_body=render_template('email/export_posts.html',
                                             user=user),
                   attachments=[('tracks.json', 'application/json',
                                 json.dumps({'tracks': data}, indent=4))],
                   sync=True)
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
