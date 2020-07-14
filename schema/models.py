from misc.config import database as db


class User(db.Document):
    userId = db.StringField(required=True, unique=True)
    username = db.StringField(required=True, unique=True)
    email = db.StringField(unique=True, max_length=30)
    password = db.StringField()
    role = db.IntField()  # 1 = admin, 2 = User


# class Director(db.Document):
#     directorId = db.StringField(required=True, unique=True)
#     name = db.StringField(max_length=50)


class Movie(db.Document):
    movieId = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    genre = db.ListField()
    imdb_score = db.DecimalField()
    popularity = db.IntField()
    director = db.StringField()
