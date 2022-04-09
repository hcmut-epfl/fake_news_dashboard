from wtforms import Form, StringField, TextAreaField, BooleanField, IntegerField

class PostForm(Form):
    text = TextAreaField('Text')
    url = StringField('URL')
    time = StringField('Uploaded Time')
    comments_count = IntegerField('Comments Count')
    reactions_count = IntegerField('Reactions Count')
    shares_count = IntegerField('Shares Count')
    comments = TextAreaField('Comments')
    true_news = BooleanField('True News Or Not?')
    claim_info = TextAreaField('Claims', description='You must input your claim to verify your confirmation')