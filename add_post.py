from src.app import db 
from src.model.post import Post
import pickle
import sys 
from tqdm import tqdm 

for data in range(1):
    p = Post(
            id=1,
            time='2020-11-04 12:22:22',
            text='Huhu',
            url='https://www.facebook.com/huhupost',
            comments_count=1030,
            reactions_count=64,
            shares_count=25,
            comments=None,
            true_news=True,
            claim_info='It is definitely true'
        )
    db.session.add(p)
    db.session.commit()