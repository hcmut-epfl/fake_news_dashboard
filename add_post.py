from datetime import datetime
from src.app import db 
from src.model.post import Post
import pickle
import sys 
from tqdm import tqdm 

for data in range(1):
    p = Post(
            id=1,
            time=datetime(2022, 5, 1, 11, 3, 24),
            text='Huhu',
            url='https://www.facebook.com/huhupost',
            comments_count=1030,
            reactions_count=64,
            shares_count=25,
            comments=None,
            true_news=True,
            group_name='Tám chuyện chơi',
            medical_news=False,
            claim_info='It is definitely true'
        )
    db.session.add(p)
    db.session.commit()