from wtforms import Form, StringField, TextAreaField, BooleanField, IntegerField

class PostForm(Form):
    text = TextAreaField('Text')
    url = StringField('URL')
    group_name = StringField('From group')
    time = StringField('Uploaded time')
    comments_count = IntegerField('Comments count')
    reactions_count = IntegerField('Reactions count')
    shares_count = IntegerField('Shares count')
    comments = TextAreaField('Comments')
    medical_news = BooleanField('Is this a medical news?')
    true_news = BooleanField('Is this a true news?')
    claim_info = TextAreaField('Claims to verify your evaluation')