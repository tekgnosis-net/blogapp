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

# Use environment variable for database URI if provided (for Docker)
db_uri = os.environ.get('DATABASE_URI')
if db_uri:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
elif(local_server==True):
    #Replace the ip_address and cloud instance and db name accordingly.
    app.config["SQLALCHEMY_DATABASE_URI"]= "mysql+mysqldb://username:password@sql_instace_IP:3306/SQL_instancename?unix_socket=/cloudsql/projectid:us-central1:codingthunder"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=True

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
    
#After first insertion , comment out the below line
create_table()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 80))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)

