"""
Loads the temporary data on the db.

format of movie object = {
    "name": string,
    "genre": array of genres,
    "director": string,
    "popularity": number,
    "imdb_score": number
}
"""

from pymongo import MongoClient
import json
import os
from misc.config import (DATABASE_NAME, PASSWORD)
from schema.validation import validate_movie
from pymongo.errors import BulkWriteError
from misc.functions import generate_string


filename = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'data.json')


def load_data():
    try:
        connection = MongoClient("mongodb+srv://root:" + PASSWORD + "@sharedit.61cic.mongodb.net/" + DATABASE_NAME + "?retryWrites=true&w=majority")
        print(connection.test)
        db = connection[DATABASE_NAME]
        movies = []
        with open(filename) as blog_file:
            data = json.load(blog_file)

        for movie in data:
            res = validate_movie(movie)
            if res['ok']:
                movie['movieId'] = generate_string()
                movies.append(movie)

        movie = db.movie

        try:
            movie.insert_many(movies)
        except BulkWriteError as bwe:
            return {'ok': False, 'message': str(bwe.details)}

        return {'ok': True, 'message': 'Data Loaded Successfully'}
    except Exception as e:
        return {'ok': False, 'message': str(e.details)}
