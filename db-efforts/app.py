from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os
DB_FILE = os.path.join(os.getcwd(), 'cd.sqlite')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_FILE

db = SQLAlchemy(app)

migrate = Migrate(app, db)
