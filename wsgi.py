from src.app import app
from src.posts.blueprint import posts
from src.ml.medical_classifier import preprocess
import __main__

__main__.preprocess = preprocess
app.register_blueprint(posts)