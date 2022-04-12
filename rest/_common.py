# rest/common.py
from functools import wraps
import json
import logging
import traceback
from flask import request, Response, jsonify
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from numpy import iterable
            

# build response
def get_response(obj):
    if type(obj) is dict:
        return Response(json.dumps(obj), mimetype="application/json", status=200)
    elif type(obj) is str:
        return Response(obj, mimetype="application/json", status=200)
    else:
        return Response(obj.to_json(), mimetype="application/json", status=200)


# build error json
def handle_error(text): 
    logging.error(traceback.format_exc())
    return { "error": text }, 200


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
                #return jsonify(msg="This action can be performed by an administrator only!"), 403 # does not work
                return "This action can be performed by an administrator only!", 403
        return decorator
    return wrapper

