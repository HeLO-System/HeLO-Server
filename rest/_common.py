# rest/common.py
import json
from functools import wraps

from flask import Response, abort
from flask_jwt_extended import get_jwt, verify_jwt_in_request

# build response
from rest.users import Role

from ._error_handling import handle_error


def get_response(obj, status=200):
    if type(obj) is dict:
        return Response(json.dumps(obj), mimetype="application/json", status=status)
    elif type(obj) is str:
        return Response(obj, mimetype="application/json", status=status)
    else:
        return Response(obj.to_json(), mimetype="application/json", status=status)


# check for None or empty string
def empty(s: str):
    if s is None or s == "" or s == " ":
        return True
    return False


# custom decorator verifying JWT is present in the request,
# as well as insuring that the request has a claim indicating
# the user is an admin
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            for r in claims["roles"]:
                if r == Role.Admin.value:
                    return fn(*args, **kwargs)
            return handle_error(f"Authorization failed", 401)
        return decorator
    return wrapper


def validate_schema(schema, args):
    errors = schema.validate(args)
    if errors: abort(400, str(errors))

