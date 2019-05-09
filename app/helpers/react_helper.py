from flask import jsonify


def is_iterable(item):
    try:
        iter(item)
        return True
    except TypeError:
        return False


def as_json(item):
    if is_iterable(item):
        return jsonify({i.id: i.serialize() for i in item})
    return jsonify(item.serialize())
