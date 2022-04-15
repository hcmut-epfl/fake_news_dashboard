import os

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://xqsdykwkanhkoi:80f2d514c8345ccec0884b91e9ae6bb056cad79d6282b31cfc0c0ad47d2bf96d@ec2-34-207-12-160.compute-1.amazonaws.com:5432/d2i1bmnt9p65kt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY='vnepfl'
    SECURITY_PASSWORD_SALT='hoangdzung'
    SECURITY_PASSWORD_HASH='sha512_crypt'