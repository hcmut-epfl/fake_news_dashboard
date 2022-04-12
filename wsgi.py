from src.app import app
from src.posts.blueprint import posts


app.register_blueprint(posts)