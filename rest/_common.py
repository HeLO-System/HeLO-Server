# rest/common.py
from functools import wraps
import json
import logging
import traceback
from flask import Response, abort
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
            

# build response
def get_response(obj, status=200):
    if type(obj) is dict:
        return Response(json.dumps(obj), mimetype="application/json", status=status)
    elif type(obj) is str:
        return Response(obj, mimetype="application/json", status=status)
    else:
        return Response(obj.to_json(), mimetype="application/json", status=status)


# build error json
# add_info, reserved, will be used later ... maybe
def handle_error(text, status=400, add_info=None): 
    logging.error(traceback.format_exc())
    if add_info is None:
        return {"error": text}, status


# check for None or empty string
def empty(s: str):
    if s is None:
        return True
    elif s == "":
        return True
    elif s == " ":
        return True
    return False


# custom decorator varifying JWT is present in the request,
# as well as insuring that the request has a claim indicating
# the user is an admin
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["is_admin"]:
                return fn(*args, **kwargs)
            else:
                #return "This action can be performed by an administrator only!", 401
                return handle_error(f"Authorization failed", 401)
        return decorator
    return wrapper


def validate_query(schema, args):
    errors = schema.validate(args)
    if errors: abort(400, str(errors))

