from src.app import app, db  
from src.routes import api
from src.posts.blueprint import posts
from src.ml.medical_classifier import preprocess

app.register_blueprint(posts)

if __name__ =='__main__':
    app.run()