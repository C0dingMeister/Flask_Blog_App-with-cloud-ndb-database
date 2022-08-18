from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Email,Length,EqualTo,ValidationError



class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired(),Length(min=4,max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password =  PasswordField('Password',validators=[DataRequired(),Length(min=6,max=20)])
    confirm_password =  PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    signup = SubmitField('Sign Up')
    # def validate_username(self,username):
    #     user = User.query().filter(User.name == username.data)
    #     if user:
    #         raise ValidationError('That username is already taken!!')
    # def validate_email(self,email):
    #     user = User.query().filter(User.name == email.data)
    #     if user:
    #         raise ValidationError('That email is already registered!!')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password =  PasswordField('Password',validators=[DataRequired()])
    remember= BooleanField('Remember Me')
    login = SubmitField('Log in')