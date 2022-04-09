from flask import Flask

from flask_admin import Admin

from flask_migrate import Migrate

from flask_script import Manager

from flask_security import SQLAlchemyUserDatastore, Security, current_user
from flask_sqlalchemy import SQLAlchemy

from src.cfg.config import Config

from src.view.admin_view import HomeAdminView, PostAdminView

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
from src.model import *
migrate = Migrate(app, db)
manager = Manager(app)

admin = Admin(
    app,
    'FlaskApp',
    url='/',
    index_view=HomeAdminView(name='Home')
)
admin.add_view(PostAdminView(Post, db.session))
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)