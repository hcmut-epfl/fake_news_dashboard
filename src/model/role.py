from flask_security import RoleMixin
from src.app import db_admin

class Role(db_admin.Model, RoleMixin):
    id = db_admin.Column(db_admin.Integer, primary_key=True)
    name = db_admin.Column(db_admin.String(100), unique=True)