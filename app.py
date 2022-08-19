############-----------------------------------------------------------IMPORTS--------------------------------------------------------######

import os
from dotenv import load_dotenv
import mock
from flask import Flask, render_template, request,redirect,url_for,flash,session,abort
import google.auth.credentials
from google.cloud import ndb
from datetime import datetime
from forms import RegistrationForm,LoginForm,CreatePostForm 
from flask_bcrypt import Bcrypt
import uuid
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

os.environ["DATASTORE_DATASET"] = "test"
os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8001"
os.environ["DATASTORE_EMULATOR_HOST_PATH"] = "localhost:8001/datastore"
os.environ["DATASTORE_HOST"] = "http://localhost:8001"
os.environ["DATASTORE_PROJECT_ID"] = "test"

credentials = mock.Mock(spec=google.auth.credentials.Credentials)
client = ndb.Client(project="test", credentials=credentials)


class User(ndb.Model):
    user_id = ndb.StringProperty()
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    date = ndb.DateTimeProperty(default=datetime.now())
  

class Blog(ndb.Model):
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    author = ndb.StringProperty()
    date = ndb.DateTimeProperty()

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
bcrypt = Bcrypt(app)

############-----------------------------------------------------------ROUTES--------------------------------------------------------######


@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        with client.context():
           
            if User.query(User.name==form.name.data).get() is not None:
                
                flash("Username already exists!!",'danger')
                return redirect(url_for('register'))
            elif User.query(User.email==form.email.data).get() is not None:
                flash("This Email is already registered!!","danger")
                return redirect(url_for('register'))

            
            user = User(user_id=uuid.uuid4().hex,
            name=form.name.data, 
            email=form.email.data,
             password=hashed_password,
             date=datetime.now()
             )
            
            user.put()
            
            flash(f'Account Created for {form.name.data}!','success')
            return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    # with client.context():
    if 'username' in session:
        print(f'Logged in as {session["username"]}')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        with client.context():
            user = User.query(User.email==form.email.data).get()
            if user and bcrypt.check_password_hash(user.password,form.password.data):
                session['username'] = user.name
                
                print("Correctomundo")
                
                return redirect(url_for('index'))
        
        flash("Login failed. Please check your login details again",'danger')
    return render_template('login.html',form=form)


@app.route('/logout',methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/")
@app.route("/home")
def index():
    user = None
    if 'username' in session:
        user = session["username"]
    
    with client.context():
        blogs = Blog.query().iter()
        return render_template('home.html', user=user,blogs=blogs)

@app.route("/create",methods=['GET','POST'])
def create():
    if 'username' in session:
        user = session["username"]
        form=CreatePostForm()
        if form.validate_on_submit():
            print(form.title.data)
            print(form.body.data)
            with client.context():
                post = Blog(title=form.title.data,
                body=form.body.data, 
                author=user,
                date=datetime.now()
                )
                post.put()
                flash("Your blog has been posted",'success')
            return redirect(url_for('create'))
        return render_template('create_posts.html',form=form,user=user)
    flash("You need to be logged in to view this page","info")
    return redirect(url_for("index"))


@app.route('/myposts')
def user_posts():
    if 'username' in session:
        user = session["username"]
        with client.context():
            blogs = Blog.query(Blog.author==user)

            return render_template('myposts.html',user=user,blogs=blogs)

    flash("You need to be logged in first","info")
    return redirect(url_for('index'))

@app.route('/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    if 'username' in session:
        user = session["username"]
        title = request.args.get('title')
        body = request.args.get('body').rstrip()
        
        with client.context():
            blog = Blog.get_by_id(id)
            if blog.author != user:
                return abort(403)
            form=CreatePostForm()
            
            if form.validate_on_submit():
                print(form.title.data)
                print(form.body.data)
                blog.title = form.title.data
                blog.body = form.body.data
                blog.put()
                flash("Post updated","success")
                return redirect(url_for('user_posts'))
        return render_template('edit.html',user=user,form=form,title=title,body=body)
            

@app.route('/delete/<int:id>',methods=['POST'])
def delete(id):
    if 'username' in session:
        user=session['username']
        with client.context():
            blog = Blog.get_by_id(id)
            blog.key.delete()
            flash("Post Deleted","success")
        return redirect(url_for('user_posts'))


if __name__ == '__main__':
    app.run(debug=True)