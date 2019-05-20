from flask import request


def get_token():
    auth_header = request.headers.get('Authorization')
    return auth_header.split(" ")[1] if auth_header else ''
