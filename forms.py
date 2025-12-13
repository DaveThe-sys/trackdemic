from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, EmailField, SelectField
from wtforms.validators import InputRequired, Length, NumberRange, DataRequired

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=30)])
    email = EmailField('Email', validators=[InputRequired(), Length(min=5, max=150)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=50)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class StudyForm(FlaskForm):
    subject = SelectField("Subject",coerce=int,validators=[InputRequired()])
    minutes = IntegerField("Minutes", validators=[DataRequired(),NumberRange(min=0, max=300, message="Minutes must be between 0 and 300.")])
    submit = SubmitField("Add Study Log")