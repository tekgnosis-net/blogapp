from flask import Flask,render_template,request,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os



with open('config.json','r') as c:
    params = json.load(c)["params"]

local_server = True
db = SQLAlchemy()

app = Flask(__name__,template_folder='template')

# Database configuration with environment variable priority
db_uri = os.environ.get('DATABASE_URI')
if db_uri:
    # Use DATABASE_URI from environment (Docker, GCP, etc.)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
elif os.environ.get('CLOUD_SQL_CONNECTION_NAME'):
    # GCP Cloud SQL via Unix socket
    connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
    db_user = os.environ.get('DB_USER', 'root')
    db_pass = os.environ.get('DB_PASS', '')
    db_name = os.environ.get('DB_NAME', 'codingthunder')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqldb://{db_user}:{db_pass}@localhost/{db_name}?unix_socket=/cloudsql/{connection_name}"
elif(local_server==True):
    # Local development fallback
    app.config["SQLALCHEMY_DATABASE_URI"]= "mysql+mysqldb://root:@localhost/codingthunder"
else:
    # Use config.json prod_uri
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db.init_app(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_num = db.Column(db.String(12),  nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime)
   
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content= db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime)

# Set up models

def create_table():
    with app.app_context():
        # Create the table in the database
        db.create_all()

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/contact', methods=['GET','POST'])
def contact():    
    if(request.method=="POST"):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get("message")

        entry = Contacts(name=name,email=email,phone_num=phone,mes=message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html',params=params)


@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post=post)
    
# Only create tables if explicitly requested (for initial setup)
if os.environ.get('CREATE_TABLES', 'False').lower() == 'true':
    create_table()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)

