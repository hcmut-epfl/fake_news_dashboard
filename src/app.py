from flask import Flask

from flask_pymongo import PyMongo

from flask_admin import Admin

from flask_migrate import Migrate

from flask_script import Manager

from flask_security import SQLAlchemyUserDatastore, Security, current_user
from flask_sqlalchemy import SQLAlchemy

from src.cfg.config import Config

from src.view.admin_view import HomeAdminView, PostAdminView

app = Flask(__name__)
app.config.from_object(Config)

client = PyMongo(app)
db = client.db
# db = MongoAlchemy(app)
db_admin = SQLAlchemy(app)
from src.model import *
migrate = Migrate(app, db_admin)
manager = Manager(app)

admin = Admin(
    app,
    'FlaskApp',
    url='/fakenews',
    index_view=HomeAdminView(name='Home')
)
# admin.add_view(PostAdminView(Post, db.session))
user_datastore = SQLAlchemyUserDatastore(db_admin, User, Role)
security = Security(app, user_datastore)