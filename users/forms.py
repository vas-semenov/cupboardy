from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField
from wtforms.validators import InputRequired, EqualTo, Email, Length, ValidationError
import re


class RegisterForm(FlaskForm):
    email = EmailField(validators=[InputRequired()])
    firstname = StringField(validators=[InputRequired()])
    password = PasswordField(validators=[InputRequired()])
    email = EmailField(validators=[InputRequired()])
    submit = SubmitField("register")

class LoginForm(FlaskForm):
    loginEmail = EmailField(validators=[InputRequired()])
    loginPassword = PasswordField(validators=[InputRequired()])
    submit = SubmitField()

class ChangePassword(FlaskForm):
    password = StringField()
    confirm_password = StringField()
    submit = SubmitField()
class ChangePasswordEmail(FlaskForm):
    email = EmailField()
    submit = SubmitField()