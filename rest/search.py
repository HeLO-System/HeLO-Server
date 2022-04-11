# rest/search.py

from flask_restful import Resource
from flask import request


class SearchApi(Resource):

    def get(self):
        # example: '/search?select=core&type=clan,match
        # keyword to look for
        select = request.args.get("select")
        # list of types to search across
        type = request.args.get("type")

        print(select, type)

        return '', 200
