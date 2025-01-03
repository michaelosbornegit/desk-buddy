from flask import jsonify


def bad_request(message):
    response = jsonify({"message": message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({"message": message})
    response.status_code = 401
    return response
