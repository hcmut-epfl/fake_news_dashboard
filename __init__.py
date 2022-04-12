from src.app import app
from src.posts.blueprint import posts


def getApp():
    app.register_blueprint(posts, url_prefix='/news')
    return app