from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

user_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "password": {
            "type": "string",
            "minLength": 5
        },
        "username": {
            "type": "string",
            "maxLength": 20
        },
        "role": {
            "type": "number"
        }
    },
    "required": ["email", "password"],
    "additionalProperties": False
}


def validate_user(data):
    try:
        validate(data, user_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


movie_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
        },
        "director": {
            "type": "string"
        },
        "popularity": {
            "type": "number",
        },
        "imdb_score": {
            "type": "number"
        },
        "genre": {
            "type": "array"
        }
    },
    "required": ["name", "director", 'genre'],
    "additionalProperties": False
}


movie_update_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
        },
        "director": {
            "type": "string"
        },
        "popularity": {
            "type": "number",
        },
        "imdb_score": {
            "type": "number"
        },
        "genre": {
            "type": "array"
        }
    },
    "additionalProperties": False
}


def validate_movie(data):
    try:
        validate(data, movie_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


def validate_update_movie(data):
    try:
        validate(data, movie_update_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}
