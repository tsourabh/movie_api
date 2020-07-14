from flask import request, jsonify
from schema.models import Movie, User
from misc.config import *
from schema.validation import validate_movie, validate_user, validate_update_movie
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity)

from permissions import admin_required
import json
from misc.functions import generate_string
# from misc.load import load_data as load_data

initialize_db(app)


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to Movie API Service. Please Use Postman to use API'})


@app.route('/api/movies', methods=['POST'])
@admin_required
def add_movie():
    """
    add movie with details according to the schema
    :return: 200 {'ok':True}
    """
    try:
        body = request.get_json()
        body = validate_movie(body)
        if body['ok']:
            body = body['data']
            unique_id = generate_string()
            while True:
                exists = Movie.objects(movieId=unique_id)
                if exists:
                    unique_id = generate_string()
                else:
                    break
            body['movieId'] = unique_id
            movie = Movie(**body).save()
            movie.save()
            return jsonify({'message': 'Movie created successfully!', 'ok': True, 'movieId': movie.movieId}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(body['message'])}), 400
    except Exception as e:
        return jsonify({'ok': False, 'message': str(e)}), 500


@app.route('/api/movies/<movie_id>', methods=['PUT', 'DELETE'])
@admin_required
def update_movie(movie_id):
    """
    update or delete movie according to the request method.
    :param movie_id: movieId
    :return: 200 {'ok':True}
    """
    try:
        if request.method == 'PUT':

            body = request.get_json()
            body = validate_update_movie(body)
            if body['ok']:
                body = body['data']
                movie = Movie.objects(movieId=movie_id)
                if movie:
                    movie = Movie.objects.get(movieId=movie_id).update(**body)
                    return jsonify({'ok': True, 'movie': movie}), 200
                else:
                    return jsonify({'ok': False, 'message': 'Movie with given Id doesn\'t exists.'}), 400
            else:
                return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(body['message'])}), 400

        elif request.method == 'DELETE':

            movie = Movie.objects(movieId=movie_id)
            if movie:
                Movie.objects.get(movieId=movie_id).delete()
                return jsonify({'ok': True}), 200
            else:
                return jsonify({'ok': False, 'message': 'Movie with given Id doesn\'t exists.'}), 400

        else:
            return jsonify({'message':'Invalid Request Type'})

    except Exception as e:
        return jsonify({'ok': False, 'message': str(e)}), 500


@app.route('/api/movies/<movie_id>', methods=['GET'])
@jwt_required
def get_movie(movie_id):
    """
    Get perticular movie details by movieId
    :param movie_id: movie id
    :return: movie object
    """
    try:
        movie = Movie.objects(movieId=movie_id)
        if movie:
            movie = Movie.objects.get(movieId=movie_id)
            return jsonify({'ok': True, 'movie': movie}), 200
        else:
            return jsonify({'ok': False, 'message': 'Movie with given Id doesn\'t exists.'}), 400
    except Exception as e:
        return jsonify({'ok': False, 'message': str(e)}), 500


@app.route('/api/search/movies', methods=['GET'])
@jwt_required
def search_movie():
    """
    Search for movies with query parameter in GET request
    :return: result set of movies matching the query term to name.
    """
    try:
        term = request.args.get('query')
        movies = Movie.objects(name__icontains=term)
        return {'result': movies, 'count': len(movies)}, 200
    except Exception as e:
        return jsonify({'ok': False, 'message': str(e)}), 500


def register(data, role):
    """
    Common function to create user
    :param data: user data
    :param role: admin/user role 1=Admin, 2=User
    :return:
    """
    data = validate_user(data)
    if data['ok']:
        data = data['data']
        data['role'] = role
        data['password'] = flask_bcrypt.generate_password_hash(data['password'])
        data['userId'] = generate_string()
        user = User.objects(username=data['username'])
        if user:
            return {'ok': False, 'message': 'Account with this username already exists!'}
        user = User.objects(email=data['email'])
        if user:
            return {'ok': False, 'message': 'Account with this email already exists!'}

        User(**data).save()

        return {'ok': True, 'message': 'User created successfully!'}
    else:
        return {'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}


@app.route('/register/admin', methods=['POST'])
def register_admin():
    """
    register admin endpoint. READ/WRITE CAPABILITY
    :return: admin creation response
    """
    response = register(request.get_json(), 1)
    if response['ok']:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route('/register/user', methods=['POST'])
def register_user():
    """
    Register user endpoint. Only has READ CAPABILITY.
    Can only be created with admin privileges.
    :return: user creation response
    """
    response = register(request.get_json(), 0)
    if response['ok']:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    """
    Add admin role to the access token. Useful when accessing APIs with admin privilege.
    :param identity:
    :return:
    """
    if identity['role'] == 1:
        return {'roles': 'admin'}
    else:
        return {'roles': 'peasant'}


@app.route('/login', methods=['POST'])
def login():
    """
    Login Endpoint
    :return: JWT Token
    """
    data = validate_user(request.get_json())
    if data['ok']:
        data = data['data']
        try:
            user = User.objects.get(email=data['email'])

            if user and flask_bcrypt.check_password_hash(user['password'], data['password']):
                user = json.loads(user.to_json())
                del user['password']
                data['role'] = user['role']
                access_token = create_access_token(identity=data)
                refresh_token = create_refresh_token(identity=data)
                user['token'] = access_token
                user['refresh'] = refresh_token
                return jsonify({'ok': True, 'data': user}), 200
            else:
                return jsonify({'ok': False, 'message': 'invalid username or password'}), 401
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 401
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """
    refresh JWT token
    :return: JWT token
    """
    current_user = get_jwt_identity()
    ret = {
            'token': create_access_token(identity=current_user)
    }
    return jsonify({'ok': True, 'data': ret}), 200


# @app.route('/load', methods=['POST'])
# @admin_required
# def load_movies():
#     try:
#         res = load_data()
#         return jsonify(res), 200
#     except Exception as e:
#         return jsonify({'ok': False, 'message': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(PORT))
