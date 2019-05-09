from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL, ValidationError

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class TrackForm(FlaskForm):
    number = StringField('Track Number',
                         validators=[DataRequired(), Regexp(regex=r'[A-Z]{2}\d{9}[A-Z]{2}',
                                                            message='Invalid track format')])
    image_url = StringField('Image URL', validators=[URL(), Optional()])
    title = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')


class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
