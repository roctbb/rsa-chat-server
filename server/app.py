from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from flask import Flask
from config import DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255))
    open_exponent = db.Column(db.Text)
    module = db.Column(db.Text)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    sender = db.Column(db.String(255))
    receiver = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, server_default=db.func.now())

db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string

db.init_app(app)
migrate = Migrate(app, db)