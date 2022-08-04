# rest/statistics.py
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest
from mongoengine.queryset.visitor import Q
import numpy as np

from models.clan import Clan
from models.console.console_clan import ConsoleClan
from models.match import Match
from models.console.console_match import ConsoleMatch
from schemas.query_schemas import StatisticsQuerySchema
from ._common import get_response, handle_error, empty, validate_schema


###############################################
#                   PC APIs                   #
###############################################

class WinrateApi(Resource):

    def get(self, oid):
        try:
            validate_schema(StatisticsQuerySchema(), request.args)
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
            validate_schema(StatisticsQuerySchema(), request.args)
            # for winrate per map
            map = request.args.get("map")
            # for winrate per side, allowed values: Axis, Allies
            side = request.args.get("side")

            clan = Clan.objects.get(id=oid)

            # if a side has been specified, the clan id must be on that side
            side_cond1 = Q(clans1_ids=str(clan.id)) & Q(side1__iexact=side)
            side_cond2 = Q(clans2_ids=str(clan.id)) & Q(side2__iexact=side)

            filter = Q()

            if not empty(map): filter &= Q(map__iexact=map)
            if not empty(side): filter &= (side_cond1 | side_cond2)

            # 5-0 victories
            vic_5 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=5))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=5)))
                                        & filter).count()
            # 4-1 victories
            vic_4 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=4))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=4)))
                                        & filter).count()
            # 3-2 victories
            vic_3 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=3))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=3)))
                                        & filter).count()
            # 2-3 defeats
            def_2 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=2))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=2)))
                                        & filter).count()
            # 1-4 defeats
            def_1 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=1))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=1)))
                                        & filter).count()
            # 0-5 defeats
            def_0 = Match.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=0))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=0)))
                                        & filter).count()
            
            total = def_0 + def_1 + def_2 + vic_3 + vic_4 + vic_5
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
                },
                "2-3": {
                    "count": def_2,
                    "share": round(def_2 / total, 3)
                },
                "1-4": {
                    "count": def_1,
                    "share": round(def_1 / total, 3)
                },
                "0-5": {
                    "count": def_0,
                    "share": round(def_0 / total, 3)
                }
            })



class PerformanceRatingApi(Resource):

    def get(self, oid):
        try:
            clan = Clan.objects.get(id=oid)
            matches_side1 = Match.objects(Q(clans1_ids=str(clan.id)))
            matches_side2 = Match.objects(Q(clans2_ids=str(clan.id)))

            strengths = []
            for match in matches_side1:
                scores = [Clan.objects.get(id=clan_id).score for clan_id in match.clans2_ids]
                strengths.append(np.average(scores))
            for match in matches_side2:
                scores = [Clan.objects.get(id=clan_id).score for clan_id in match.clans1_ids]
                strengths.append(sum(scores)/len(scores))

            # get all matches where the clan was either on side1 and caps1 > caps2 (condition 1)
            # or on side2 and caps1 < caps2 (condition 2)
            win_cond1 = Q(clans1_ids=str(clan.id)) & Q(caps1__gte=3)
            win_cond2 = Q(clans2_ids=str(clan.id)) & Q(caps2__gte=3)

            total = clan.num_matches
            wins = Match.objects(win_cond1 | win_cond2).count()

            pr = (sum(strengths) + 400 * (wins - (total - wins))) / total
            
            return get_response({"pr": round(pr, 2)})
                
        except ValidationError as e:
            return handle_error(f"validation failed: {e}", 400)
        except BadRequest as e:
            return handle_error(f"Bad Request, terminated with: {e}", 400)
        except Exception as e:
            return handle_error(f"error fetching items from database, terminated with error: {e}", 500)



###############################################
#                CONSOLE APIs                 #
###############################################

class ConsoleWinrateApi(Resource):

    def get(self, oid):
        try:
            validate_schema(StatisticsQuerySchema(), request.args)
            # for winrate per map
            map = request.args.get("map")
            # for winrate per side, allowed values: Axis, Allies
            side = request.args.get("side")

            clan = ConsoleClan.objects.get(id=oid)
            # get all matches where the clan was either on side1 and caps1 > caps2 (condition 1)
            # or on side2 and caps1 < caps2 (condition 2)
            win_cond1 = Q(clans1_ids=str(clan.id)) & Q(caps1__gte=3)
            win_cond2 = Q(clans2_ids=str(clan.id)) & Q(caps2__gte=3)

            # if a side has been specified, the clan id must be on that side
            side_cond1 = Q(clans1_ids=str(clan.id)) & Q(side1__iexact=side)
            side_cond2 = Q(clans2_ids=str(clan.id)) & Q(side2__iexact=side)

            # only map is specified
            if not empty(map) and empty(side):
                total = ConsoleMatch.objects((Q(clans1_ids=str(clan.id)) | Q(clans2_ids=str(clan.id)))
                                        & Q(map__iexact=map)).count()
                wins = ConsoleMatch.objects((win_cond1 | win_cond2) & Q(map__iexact=map)).count()

            # only side is specified
            elif not empty(side) and empty(map):
                total = ConsoleMatch.objects(side_cond1 | side_cond2).count()
                wins = ConsoleMatch.objects((win_cond1 | win_cond2) & (side_cond1 | side_cond2)).count()

            # map and side are specified
            elif not empty(map) and not empty(side):
                total = ConsoleMatch.objects((side_cond1 | side_cond2) & Q(map__iexact=map)).count()
                wins = ConsoleMatch.objects((win_cond1 | win_cond2) & (side_cond1 | side_cond2)
                                    & Q(map__iexact=map)).count()

            # neither map nor side is specified, user requested general winrate
            else:
                total = clan.num_matches
                wins = ConsoleMatch.objects((win_cond1 | win_cond2)).count()

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


class ConsoleResultTypesApi(Resource):

    def get(self, oid):
        try:
            validate_schema(StatisticsQuerySchema(), request.args)
            # for winrate per map
            map = request.args.get("map")
            # for winrate per side, allowed values: Axis, Allies
            side = request.args.get("side")

            clan = ConsoleClan.objects.get(id=oid)

            # if a side has been specified, the clan id must be on that side
            side_cond1 = Q(clans1_ids=str(clan.id)) & Q(side1__iexact=side)
            side_cond2 = Q(clans2_ids=str(clan.id)) & Q(side2__iexact=side)

            filter = Q()

            if not empty(map): filter &= Q(map__iexact=map)
            if not empty(side): filter &= (side_cond1 | side_cond2)

            # 5-0 victories
            vic_5 = ConsoleMatch.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=5))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=5)))
                                        & filter).count()
            # 4-1 victories
            vic_4 = ConsoleMatch.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=4))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=4)))
                                        & filter).count()
            # 3-2 victories
            vic_3 = ConsoleMatch.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=3))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=3)))
                                        & filter).count()
            # 2-3 defeats
            def_2 = ConsoleMatch.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=2))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=2)))
                                        & filter).count()
            # 1-4 defeats
            def_1 = ConsoleMatch.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=1))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=1)))
                                        & filter).count()
            # 0-5 defeats
            def_0 = ConsoleMatch.objects(((Q(clans1_ids=str(clan.id)) & Q(caps1=0))
                                        | (Q(clans2_ids=str(clan.id)) & Q(caps2=0)))
                                        & filter).count()
            
            total = def_0 + def_1 + def_2 + vic_3 + vic_4 + vic_5
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
                },
                "2-3": {
                    "count": def_2,
                    "share": round(def_2 / total, 3)
                },
                "1-4": {
                    "count": def_1,
                    "share": round(def_1 / total, 3)
                },
                "0-5": {
                    "count": def_0,
                    "share": round(def_0 / total, 3)
                }
            })



class ConsolePerformanceRatingApi(Resource):

    def get(self, oid):
        try:
            clan = ConsoleClan.objects.get(id=oid)
            matches_side1 = ConsoleMatch.objects(Q(clans1_ids=str(clan.id)))
            matches_side2 = ConsoleMatch.objects(Q(clans2_ids=str(clan.id)))

            strengths = []
            for match in matches_side1:
                scores = [ConsoleClan.objects.get(id=clan_id).score for clan_id in match.clans2_ids]
                strengths.append(np.average(scores))
            for match in matches_side2:
                scores = [ConsoleClan.objects.get(id=clan_id).score for clan_id in match.clans1_ids]
                strengths.append(sum(scores)/len(scores))

            # get all matches where the clan was either on side1 and caps1 > caps2 (condition 1)
            # or on side2 and caps1 < caps2 (condition 2)
            win_cond1 = Q(clans1_ids=str(clan.id)) & Q(caps1__gte=3)
            win_cond2 = Q(clans2_ids=str(clan.id)) & Q(caps2__gte=3)

            total = clan.num_matches
            wins = ConsoleMatch.objects(win_cond1 | win_cond2).count()

            pr = (sum(strengths) + 400 * (wins - (total - wins))) / total
            
            return get_response({"pr": round(pr, 2)})
                
        except ValidationError as e:
            return handle_error(f"validation failed: {e}", 400)
        except BadRequest as e:
            return handle_error(f"Bad Request, terminated with: {e}", 400)
        except Exception as e:
            return handle_error(f"error fetching items from database, terminated with error: {e}", 500)
