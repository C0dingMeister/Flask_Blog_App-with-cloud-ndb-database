############-----------------------------------------------------------IMPORTS--------------------------------------------------------######
import os
from dotenv import load_dotenv
import mock
from flask import Flask, render_template, request,redirect,url_for,flash,session
import google.auth.credentials
from google.cloud import ndb
from datetime import datetime
from forms import RegistrationForm,LoginForm 
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
# login_manager = LoginManager(app)

############-----------------------------------------------------------ROUTES--------------------------------------------------------######

# @login_manager.user_loader
# def load_user(user_id):
#     return User.get_by_id(user_id)



@app.route("/")
@app.route("/home")
def index():
    user = None
    if 'username' in session:
        user = session["username"]

    # with client.context():
    #     user = User.query(User.name=='player')
    #     print(user.get().key.id())
    #     print(uuid.uuid1())
    return render_template('home.html', user=user)

@app.route("/about")
def about():
    
    return render_template('about.html')


@app.route('/register',methods=['GET','POST'])
def register():
    # with client.context():
    #     if current_user.is_authenticated:
    #         return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        with client.context():  
            user_exist = User.query(User.name==form.name.data)
            
            print(user_exist.get())
            if user_exist.get() is not None:
                print("entering loop")
                # for i in user_exist.iter():
                    # print(i)
                    # print("Username Already exists!!")
                flash("Username already exists!!",'danger')
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

@app.route('/posts')
def posts():
    with client.context():
        query = User.query()
        posts = [(user.name,user.date) for user in query]
        
        return render_template('posts.html',posts=posts)
@app.route('/upload',methods=['POST'])
def upload():
    # with client.context():
    #     user_data = User(name=request.form['name'],
    #                      email=request.form['article'],
    #                      password=request.form['password'],
    #                      date=datetime.now())
    #     user_data.put()
    name = request.form['name']
    email = request.form['email']
    print(f'''
    {name}  {email}
    ''')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)