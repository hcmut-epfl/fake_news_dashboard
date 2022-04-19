from src.app import db, user_datastore

db.create_all()
email = input('Enter User Email: ')
password = input('Enter Password: ')
user = user_datastore.create_user(
    email=email,
    password=password
)
db.session.add(user)
db.session.commit()