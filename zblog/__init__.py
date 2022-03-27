from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os

app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'

load_dotenv()

# CONFIG KEYS
app.config['SECRET_KEY'] = os.getenv("SECRET")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")

db = SQLAlchemy(app)
from zblog import models
migrate = Migrate(app, db)

from zblog import routes
