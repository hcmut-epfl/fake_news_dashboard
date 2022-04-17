from src.app import db

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Text)
    text = db.Column(db.Text)
    shortened_text = db.Column(db.Text)
    url = db.Column(db.String(140))
    comments_count = db.Column(db.Integer)
    reactions_count = db.Column(db.Integer)
    shares_count = db.Column(db.Integer)
    comments = db.Column(db.Text)
    group_name = db.Column(db.Text)
    medical_news = db.Column(db.Boolean)
    true_news = db.Column(db.Boolean)
    claim_info = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        kwargs['shortened_text'] = kwargs['text'][:100]
        kwargs['comments'] = self.modify_comments(kwargs['comments'])
        super().__init__(
            *args, **kwargs
        )

    def modify_comments(self, comments):
        if comments is None:
            return ''
    
    def __repr__(self):
        return f'<Post ID: {self.id}, text: {self.text}'
