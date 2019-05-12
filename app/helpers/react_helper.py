def is_iterable(item):
    try:
        iter(item)
        return True
    except TypeError:
        return False


def as_json(item):
    if is_iterable(item):
        return {i.id: i.serialize() for i in item}
    return item.serialize()


# @auth.error_handler()
# def error_handler(callback):
#     return jsonify({
#         'ok': False,
#         'message': 'Missing Authorization Header'
#     }), 401
#

# def is_correct_token():
#     auth_header = request.headers.get('Authorization')
#     if auth_header:
#         try:
#             auth_token = auth_header.split(" ")[1]
#         except IndexError:
#             responseObject = {
#                 'status': 'fail',
#                 'message': 'Bearer token malformed.'
#             }
#             return False
#     else:
#         auth_token = ''


# def auth_required(func):
#     @wraps(func)
#     def decorated(*args, **kwargs):
#         if request.method in EXEMPT_METHODS:
#             return func(*args, **kwargs)
#         elif not current_user.is_authenticated:
#             return current_app.login_manager.unauthorized()
#         return func(*args, **kwargs)
#
#     return decorated
