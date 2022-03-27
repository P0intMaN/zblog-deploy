# pip install flask-wtf
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Please fill the field ☝"), Length(min=2, max=30, message="Username must be 2 to 30 characters long 📐")])
    email = StringField('Email', validators=[DataRequired(message="Please fill the field ☝"), Email(message="Email not valid ❌")])
    password = PasswordField('Password', validators=[DataRequired(message="Please fill the field ☝")])
    conf_password = PasswordField('Confirm Password', validators=[DataRequired(message="Please fill the field ☝"), EqualTo('password', message="Passwords did not match 🔗")])

    submit = SubmitField('Register 🤖')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Please fill the field ☝"), Email(message="Email not valid ❌")])
    password = PasswordField('Password', validators=[DataRequired(message="Please fill the field ☝")])
    rem_me = BooleanField('Remember Me')

    submit = SubmitField('Log In 🤖')

class AddTagForm(FlaskForm):
    identifier = StringField()
    new_tag_name = StringField(label='Tag Name: ', validators=[DataRequired(message='Please fill the field ☝')])

    submit = SubmitField('Add Tag')

class RemovePostForm(FlaskForm):
    identifier = StringField()
    title = StringField('Post Title: ', validators=[DataRequired(message='Please fill the field ☝')])

    submit = SubmitField('Remove')

class ConfigurePostForm(FlaskForm):
    identifier = StringField()
    post_title = StringField('Post Title: ', validators=[DataRequired(message='Please fill the field ☝')])
    tags = StringField('Tags: ', validators=[DataRequired(message='Please fill the field ☝')])

    submit = SubmitField('Save Configuration Changes')
