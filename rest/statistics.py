# rest/statistics.py
from this import d
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.queryset.visitor import Q

from models.clan import Clan
from models.match import Match
from ._common import get_response, handle_error, admin_required, empty, validate_query


class WinrateApi(Resource):

    def get(self, oid):
        try:
            # for winrate per map
            map = request.args.get("map")

            clan = Clan.objects.get(id=oid)
            # get all matches where the clan was either on side1 and caps1 > caps2 (condition 1)
            # or on side2 and caps1 < caps2 (condition 2)
            cond1 = Q(clans1_ids=str(clan.id)) & Q(caps1__gte=3)
            cond2 = Q(clans2_ids=str(clan.id)) & Q(caps2__gte=3)

            if not empty(map):
                total = Match.objects((Q(clans1_ids=str(clan.id)) | Q(clans2_ids=str(clan.id))) & Q(map__iexact=map)).count()
                wins = Match.objects((cond1 | cond2) & Q(map__iexact=map)).count()
                print(total)
            else:
                total = clan.num_matches
                wins = Match.objects((cond1 | cond2)).count()
            
            return get_response({
                "total": total,
                "wins": wins,
                "winrate": round(wins / total, 3)
            })

        except ZeroDivisionError:
            return get_response({
                "total": 0,
                "wins": 0,
                "winrate": 0
            })
