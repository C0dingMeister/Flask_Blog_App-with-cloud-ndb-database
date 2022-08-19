from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Email,Length,EqualTo,ValidationError



class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired(),Length(min=4,max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password =  PasswordField('Password',validators=[DataRequired(),Length(min=6,max=20)])
    confirm_password =  PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    signup = SubmitField('Sign Up')
   

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password =  PasswordField('Password',validators=[DataRequired()])
    remember= BooleanField('Remember Me')
    login = SubmitField('Log in')
    
class CreatePostForm(FlaskForm):
    title= StringField('Title', validators=[DataRequired(),Length(min=6,max=30)])
    body= TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
   