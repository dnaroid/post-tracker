from datetime import datetime

import requests
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.email import send_email
from app.helpers.event_helper import parse_events
from app.main import bp
from app.main.forms import EditProfileForm, TrackForm
from app.models import Event, Track, User


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = TrackForm()
    if form.validate_on_submit():
        track = Track(number=form.number.data, title=form.title.data, owner=current_user)
        db.session.add(track)
        db.session.commit()
        flash('Track added')
        print('-------current_app.config', current_app.config)
        print('-------current_app.config', current_app.config['MAIL_SERVER'])
        print('-------current_app.config', current_app.config['MAIL_USERNAME'])
        print('-------current_app.config', current_app.config['ADMINS'])
        send_email('[Tracker] track added',
                   sender='dnaroid.pythonanywhere@gmail.com', recipients=[current_user.email],
                   text_body=f'Track {track.number} {track.title} added',
                   html_body=f'Track {track.number} {track.title} added',
                   sync=False)
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    tracks = current_user.tracks.paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.index', page=tracks.next_num) \
        if tracks.has_next else None
    prev_url = url_for('main.index', page=tracks.prev_num) \
        if tracks.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           tracks=tracks.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    tracks = user.tracks.order_by(Track.timestamp.desc()).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=tracks.next_num) if tracks.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=tracks.prev_num) if tracks.has_prev else None
    return render_template('user.html', user=user, tracks=tracks.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/track/<number>')
@login_required
def track(number):
    track = Track.query.filter_by(number=number).first_or_404()
    page = request.args.get('page', 1, type=int)
    events = track.events.order_by(Event.timestamp.desc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=events.next_num) if events.has_next else None
    prev_url = url_for('main.user', username=user.username, page=events.prev_num) if events.has_prev else None

    r = requests.get(f'https://webservices.belpost.by/searchRu/{track.number}')
    events = parse_events(r.text)
    status = r.status_code
    return render_template('track.html', track=track, next_url=next_url, prev_url=prev_url, events=events)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
