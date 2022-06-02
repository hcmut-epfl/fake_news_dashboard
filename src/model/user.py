from src.app import db_admin

from flask_security import UserMixin

roles_users = db_admin.Table(
    'roles_users',
    db_admin.Column('user_id', db_admin.Integer, db_admin.ForeignKey('user.id')),
    db_admin.Column('role_id', db_admin.Integer, db_admin.ForeignKey('role.id'))
)

class User(db_admin.Model, UserMixin):
    id = db_admin.Column(db_admin.Integer, primary_key=True)
    email = db_admin.Column(db_admin.String(100), unique=True)
    password = db_admin.Column(db_admin.String(255))
    active = db_admin.Column(db_admin.Boolean)
    roles = db_admin.relationship('Role',secondary=roles_users, 
    backref=db_admin.backref('users'), lazy='dynamic')