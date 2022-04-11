# rest/search.py

from flask_restful import Resource
from flask import request

from logic._getter import get_model
from ._common import get_response


class SearchApi(Resource):

    def get(self):
        try:
            # example: '/search?select=core&type=match
            # keyword to look for
            select = request.args.get("select")
            # type to search across, allowed values: 'clan', 'match', 'score'
            t = request.args.get("type")

            if select is None or select == "" or select == " ":
                raise RuntimeError

            # https://www.tutorialspoint.com/mongoengine/mongoengine_text_search.htm
            # https://docs.mongoengine.org/guide/text-indexes.html
            # https://www.tutorialspoint.com/mongoengine/mongoengine_indexes.htm
            cls = get_model(t)
            docs = cls.objects.search_text(select)

            return get_response(docs)
        
        except ValueError:
            return {
                "error": "mandatory query paramter 'type' got an illegal value",
                "allowed_values": ["clan", "match", "score"],
                "example": ".../search?select=core&type=match"
            }, 422

        except RuntimeError:
            return {
                "error": "mandatory query paramter 'select' is 'None' or empty, please enter a keyword",
                "example": ".../search?select=core&type=match"
            }, 400
