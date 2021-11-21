# rest/common.py
import json
from flask import request, Response
from database.models import Clan
            

# build response
def get_response(obj):
    if type(obj) is dict:
        return Response(json.dumps(obj), mimetype="application/json", status=200)
    elif type(obj) is str:
        return Response(obj, mimetype="application/json", status=200)
    else:
        return Response(obj.to_json(), mimetype="application/json", status=200)


# build error json
def get_error(text): 
    return { "error": text }, 200
