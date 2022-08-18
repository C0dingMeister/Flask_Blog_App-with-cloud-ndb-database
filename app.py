import os
import mock
from flask import Flask, render_template, request,redirect,url_for
import google.auth.credentials
from google.cloud import ndb
from datetime import datetime

os.environ["DATASTORE_DATASET"] = "test"
os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8001"
os.environ["DATASTORE_EMULATOR_HOST_PATH"] = "localhost:8001/datastore"
os.environ["DATASTORE_HOST"] = "http://localhost:8001"
os.environ["DATASTORE_PROJECT_ID"] = "test"

credentials = mock.Mock(spec=google.auth.credentials.Credentials)
client = ndb.Client(project="test", credentials=credentials)


class User(ndb.Model):
    name = ndb.StringProperty()
    article = ndb.TextProperty()
    date = ndb.DateTimeProperty()

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def index():
    return render_template('home.html')

@app.route("/about")
def about():
    
    return render_template('about.html')

@app.route('/posts')
def posts():
    with client.context():
        query = User.query()
        posts = [(user.name,user.article,user.date) for user in query]
        
        return render_template('posts.html',posts=posts)
@app.route('/upload',methods=['POST'])
def upload():
    with client.context():
        user_data = User(name=request.form['name'],
                         article=request.form['article'],
                         date=datetime.now())
        user_data.put()
    name = request.form['name']
    article = request.form['article']
    print(f'''
    {name}  {article}
    ''')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)