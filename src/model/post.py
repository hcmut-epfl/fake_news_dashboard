from src.app import db

class Reaction(db.Document):

    likes = db.IntField()
    favorites = db.IntField()
    cares = db.IntField()
    hahas = db.IntField()
    wows = db.IntField()
    sads = db.IntField()
    angries = db.IntField()

class PostStat(db.Document):

    time = db.DateTimeField()
    reaction_count = db.IntField()
    comments = db.IntField()
    shares = db.IntField()
    reactors = db.AnythingField()
    reactions = db.DocumentField(Reaction)

class Comment(db.Document):
    
    info = db.DocumentField(PostStat)
    text = db.StringField()
    page_id = db.StringField()
    post_id = db.StringField()
    comment_id = db.StringField()
    comments_full = db.AnythingField()
    username = db.StringField()
    user_id = db.StringField()

class Post(db.Document):

    info = db.DocumentField(PostStat)
    comments_full = db.AnythingField()
    post_id = db.StringField()
    page_id = db.StringField()
    post_url = db.StringField()
    text = db.StringField()
    images = db.AnythingField()
    medical_label = db.BoolField()
    username = db.StringField()
    fetched_time = db.DateTimeField()
    user_id = db.StringField()

    # id = db.Column(db.Integer, primary_key=True)
    # time = db.Column(db.Text)
    # text = db.Column(db.Text)
    # shortened_text = db.Column(db.Text)
    # url = db.Column(db.String(140))
    # comments_count = db.Column(db.Integer)
    # reactions_count = db.Column(db.Integer)
    # shares_count = db.Column(db.Integer)
    # comments = db.Column(db.Text)
    # group_name = db.Column(db.Text)
    # medical_news = db.Column(db.Boolean)
    # true_news = db.Column(db.Boolean)
    # claim_info = db.Column(db.Text)

    # def __init__(self, *args, **kwargs):
    #     kwargs['shortened_text'] = kwargs['text'][:100]
    #     kwargs['comments'] = self.modify_comments(kwargs['comments'])
    #     super().__init__(
    #         *args, **kwargs
    #     )

    # def modify_comments(self, comments):
    #     if comments is None:
    #         return ''
    
    # def __repr__(self):
    #     return f'<Post ID: {self.id}, text: {self.text}'


