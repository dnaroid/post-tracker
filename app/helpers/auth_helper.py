from flask import request


def get_token():
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1] if auth_header else ''
    except IndexError:
        token = ''
    return token
