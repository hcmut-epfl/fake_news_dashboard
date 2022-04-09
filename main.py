from src.app import app, db  
from src.routes import api
from src.posts.blueprint import posts

app.register_blueprint(posts, url_prefix='/news')

if __name__ =='__main__':
    app.run()