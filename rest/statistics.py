# rest/statistics.py
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest
from mongoengine.queryset.visitor import Q

from models.clan import Clan
from models.match import Match
from schemas.query_schemas import StatisticsQuerySchema
from ._common import get_response, handle_error, empty, validate_query


class WinrateApi(Resource):

    def get(self, oid):
        try:
            validate_query(StatisticsQuerySchema(), request.args)
            # for winrate per map
            map = request.args.get("map")
            # for winrate per side, allowed values: Axis, Allies
            side = request.args.get("side")

            clan = Clan.objects.get(id=oid)
            # get all matches where the clan was either on side1 and caps1 > caps2 (condition 1)
            # or on side2 and caps1 < caps2 (condition 2)
            win_cond1 = Q(clans1_ids=str(clan.id)) & Q(caps1__gte=3)
            win_cond2 = Q(clans2_ids=str(clan.id)) & Q(caps2__gte=3)

            # if a side has been specified, the clan id must be on that side
            side_cond1 = Q(clans1_ids=str(clan.id)) & Q(side1__iexact=side)
            side_cond2 = Q(clans2_ids=str(clan.id)) & Q(side2__iexact=side)

            # only map is specified
            if not empty(map) and empty(side):
                total = Match.objects((Q(clans1_ids=str(clan.id)) | Q(clans2_ids=str(clan.id)))
                                        & Q(map__iexact=map)).count()
                wins = Match.objects((win_cond1 | win_cond2) & Q(map__iexact=map)).count()

            # only side is specified
            elif not empty(side) and empty(map):
                total = Match.objects(side_cond1 | side_cond2).count()
                wins = Match.objects((win_cond1 | win_cond2) & (side_cond1 | side_cond2)).count()

            # map and side are specified
            elif not empty(map) and not empty(side):
                total = Match.objects((side_cond1 | side_cond2) & Q(map__iexact=map)).count()
                wins = Match.objects((win_cond1 | win_cond2) & (side_cond1 | side_cond2)
                                    & Q(map__iexact=map)).count()

            # neither map nor side is specified, user requested general winrate
            else:
                total = clan.num_matches
                wins = Match.objects((win_cond1 | win_cond2)).count()

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
        except ValidationError as e:
            return handle_error(f"validation failed: {e}", 400)
        except BadRequest as e:
            return handle_error(f"Bad Request, terminated with: {e}", 400)
        except Exception as e:
            return handle_error(f"error fetching items from database, terminated with error: {e}", 500)


class ResultTypesApi(Resource):

    def get(self, oid):
        try:
            validate_query(StatisticsQuerySchema(), request.args)
            # for winrate per map
            map = request.args.get("map")
            # for winrate per side, allowed values: Axis, Allies
            side = request.args.get("side")

            clan = Clan.objects.get(id=oid)

            # if a side has been specified, the clan id must be on that side
            side_cond1 = Q(clans1_ids=str(clan.id)) & Q(side1__iexact=side)
            side_cond2 = Q(clans2_ids=str(clan.id)) & Q(side2__iexact=side)

            # only map is specified
            if not empty(map) and empty(side):
                # 5-0 victories
                vic_5 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=5))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=5)))
                                        & Q(map__iexact=map)).count()
                # 4-1 victories
                vic_4 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=4))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=4)))
                                        & Q(map__iexact=map)).count()
                # 3-2 victories
                vic_3 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=3))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=3)))
                                        & Q(map__iexact=map)).count()

            # only side is specified
            elif not empty(side) and empty(map):
                # 5-0 victories
                vic_5 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=5))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=5)))
                                        & (side_cond1 | side_cond2)).count()
                # 4-1 victories
                vic_4 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=4))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=4)))
                                        & (side_cond1 | side_cond2)).count()
                # 3-2 victories
                vic_3 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=3))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=3)))
                                        & (side_cond1 | side_cond2)).count()

            # map and side are specified
            elif not empty(map) and not empty(side):
                # 5-0 victories
                vic_5 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=5))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=5)))
                                        & (side_cond1 | side_cond2)
                                        & Q(map__iexact=map)).count()
                # 4-1 victories
                vic_4 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=4))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=4)))
                                        & (side_cond1 | side_cond2)
                                        & Q(map__iexact=map)).count()
                # 3-2 victories
                vic_3 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=3))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=3)))
                                        & (side_cond1 | side_cond2)
                                        & Q(map__iexact=map)).count()

            # neither map nor side is specified, user requested general winrate
            else:
                # 5-0 victories
                vic_5 = Match.objects((Q(clans1_ids=str(clan.id)) & Q(caps1=5))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=5))
                                        ).count()
                # 4-1 victories
                vic_4 = Match.objects((Q(clans1_ids=str(clan.id)) & Q(caps1=4))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=4))
                                        ).count()
                # 3-2 victories
                vic_3 = Match.objects((Q(clans1_ids=str(clan.id)) & Q(caps1=3))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=3))
                                        ).count()

            total = vic_3 + vic_4 + vic_5
            if total == 0: total = 1    # to avoid multiple zero division errors
                    
        except ValidationError as e:
            return handle_error(f"validation failed: {e}", 400)
        except BadRequest as e:
            return handle_error(f"Bad Request, terminated with: {e}", 400)
        except Exception as e:
            return handle_error(f"error fetching items from database, terminated with error: {e}", 500)
        else:
            return get_response({
                "5-0": {
                    "count": vic_5,
                    "share": round(vic_5 / total, 3)
                },
                "4-1": {
                    "count": vic_4,
                    "share": round(vic_4 / total, 3)
                },
                "3-2": {
                    "count": vic_3,
                    "share": round(vic_3 / total, 3)
                }
            })
