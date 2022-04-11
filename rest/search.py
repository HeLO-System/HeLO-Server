# rest/search.py

from flask_restful import Resource
from flask import request

from models.clan import Clan
from models.match import Match
from models.score import Score


def get_model(t):
    if t == "clan":
        return Clan
    elif t == "match":
        return Match
    elif t == "score":
        return Score


class SearchApi(Resource):

    def get(self):
        # example: '/search?select=core&type=clan,match
        # keyword to look for
        select = request.args.get("select")
        # list of types to search across
        t = request.args.get("type")

        print(select, t)

        # https://www.tutorialspoint.com/mongoengine/mongoengine_text_search.htm
        # https://docs.mongoengine.org/guide/text-indexes.html
        # https://www.tutorialspoint.com/mongoengine/mongoengine_indexes.htm
        docs = Match.objects.search_text(select)
        for doc in docs:
            print(doc.to_json())

        # cls, crit = get_model(t)

        # # docs = cls.objects.filter(_tag_lower=select)
        # # print(docs)

        # docs = cls.objects(crit__iexact=select)
        # print(docs)

        return '', 200
