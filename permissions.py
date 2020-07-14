from functools import wraps

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, verify_jwt_in_request, create_access_token,
    get_jwt_claims
)

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


def admin_required(fn):
    """
    Here is a custom decorator that verifies the JWT is present in
    the request, as well as insuring that this user has a role of
    `admin` in the access token
    :param fn:
    :return:
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['roles'] != 'admin':
            return jsonify(msg='This is admin only feature!'), 403
        else:
            return fn(*args, **kwargs)
    return wrapper

