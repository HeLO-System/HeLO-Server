# rest/matches.py
from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from mongoengine.errors import ValidationError, DoesNotExist

from logic.helo_functions import get_new_scores, get_coop_scores,\
                    get_new_console_scores, get_console_coop_scores
from models.clan import Clan
from models.console.console_clan import ConsoleClan
from schemas.request_schemas import SimulationsSchema, ConsoleSimulationsSchema
from schemas.query_schemas import SimulationsQuerySchema
from ._common import get_response, handle_error, validate_schema


###############################################
#                   PC APIs                   #
###############################################

class SimulationsApi(Resource):

    def get(self):
        try:
            # validate request schema
            validate_schema(SimulationsSchema(), request.get_json())
            # validate query schema
            validate_schema(SimulationsQuerySchema(), request.args)
            ignore = request.args.get("ignore")
            ignore = ignore.split(",") if ignore is not None else []

            # get clans by their provided ids
            clans1 = [Clan.objects.get(id=clan_id) for clan_id in request.get_json().get("clans1_ids")]
            clans2 = [Clan.objects.get(id=clan_id) for clan_id in request.get_json().get("clans2_ids")]

            # competitive factor, if provided
            c = 1 if request.get_json().get("factor") is None else request.get_json().get("factor")
            # number of players, if provided
            players = 50 if request.get_json().get("players") is None else request.get_json().get("players")

            # coop game
            if len(clans1) > 1 or len(clans2) > 1:
                new_scores1, new_scores2, err = get_coop_scores(
                    clan_scores1=[clan.score for clan in clans1],
                    clan_scores2=[clan.score for clan in clans2],
                    caps1=request.get_json().get("caps1"),
                    caps2=request.get_json().get("caps2"),
                    num_matches1=[clan.num_matches for clan in clans1],
                    num_matches2=[clan.num_matches for clan in clans2],
                    player_dist1=request.get_json().get("player_dist1"),
                    player_dist2=request.get_json().get("player_dist2"),
                    c=c if "factor" not in ignore else 1,
                    num_players=players if "players" not in ignore else 50
                    )

            # no coop game
            else:
                new_scores1, new_scores2, err = get_new_scores(
                    score1=clans1[0].score,
                    score2=clans2[0].score,
                    caps1=request.get_json().get("caps1"),
                    caps2=request.get_json().get("caps2"),
                    matches1=clans1[0].num_matches if "num_matches" not in ignore else 0,
                    matches2=clans2[0].num_matches if "num_matches" not in ignore else 0,
                    c=c if "factor" not in ignore else 1,
                    number_of_players=players if "players" not in ignore else 50
                    )
                # TODO: ugly, make this better
                new_scores1, new_scores2 = [new_scores1], [new_scores2]

            if err is not None: raise BadRequest("calculation failed due to logical reasons, please check your input")

            # create a dictionary with the new score and difference for every clan
            # on both sides
            clans1_mapped = [{"name": clan.tag, "new_score": new_score, "difference": new_score -  clan.score}
                            for clan, new_score in zip(clans1, new_scores1)]
            clans2_mapped = [{"name": clan.tag, "new_score": new_score, "difference": new_score -  clan.score}
                            for clan, new_score in zip(clans2, new_scores2)]
            return get_response({
                "side1": clans1_mapped,
                "side2": clans2_mapped
            })

        except BadRequest as e:
            return handle_error(f"{e}")
        except ValidationError as e:
            return handle_error(f"validation error: {e}")
        except DoesNotExist as e:
            return handle_error(f"not found: {e}", 404)
        except Exception as e:
            return handle_error(f"something went terribly wrong: {e}", 500)



###############################################
#                CONSOLE APIs                 #
###############################################

class ConsoleSimulationsApi(Resource):

    def get(self):
        try:
            # validate request schema
            validate_schema(ConsoleSimulationsSchema(), request.get_json())
            # validate query schema
            validate_schema(SimulationsQuerySchema(), request.args)
            ignore = request.args.get("ignore")
            ignore = ignore.split(",") if ignore is not None else []

            # get clans by their provided ids
            clans1 = [ConsoleClan.objects.get(id=clan_id) for clan_id in request.get_json().get("clans1_ids")]
            clans2 = [ConsoleClan.objects.get(id=clan_id) for clan_id in request.get_json().get("clans2_ids")]

            # competitive factor, if provided
            c = 1 if request.get_json().get("factor") is None else request.get_json().get("factor")
            # number of players and randoms (blueberries :D)
            players1 = 50 if request.get_json().get("players1") is None else request.get_json().get("players1")
            players2 = 50 if request.get_json().get("players2") is None else request.get_json().get("players2")
            randoms1 = 50 if request.get_json().get("randoms1") is None else request.get_json().get("randoms1")
            randoms2 = 50 if request.get_json().get("randoms2") is None else request.get_json().get("randoms2")

            # coop game
            if len(clans1) > 1 or len(clans2) > 1:
                new_scores1, new_scores2, err = get_console_coop_scores(
                    clan_scores1=[clan.score for clan in clans1],
                    clan_scores2=[clan.score for clan in clans2],
                    caps1=request.get_json().get("caps1"),
                    caps2=request.get_json().get("caps2"),
                    num_matches1=[clan.num_matches for clan in clans1],
                    num_matches2=[clan.num_matches for clan in clans2],
                    player_dist1=request.get_json().get("player_dist1"),
                    player_dist2=request.get_json().get("player_dist2"),
                    c=c if "factor" not in ignore else 1,
                    n1=players1,
                    t1=randoms1,
                    n2=players2,
                    t2=players1
                    )

            # no coop game
            else:
                new_scores1, new_scores2, err = get_new_console_scores(
                    score1=clans1[0].score,
                    score2=clans2[0].score,
                    caps1=request.get_json().get("caps1"),
                    caps2=request.get_json().get("caps2"),
                    matches1=clans1[0].num_matches if "num_matches" not in ignore else 0,
                    matches2=clans2[0].num_matches if "num_matches" not in ignore else 0,
                    c=c if "factor" not in ignore else 1,
                    n1=players1,
                    t1=randoms1,
                    n2=players2,
                    t2=players1
                    )
                # TODO: ugly, make this better
                new_scores1, new_scores2 = [new_scores1], [new_scores2]

            if err is not None: raise BadRequest("calculation failed due to logical reasons, please check your input")

            # create a dictionary with the new score and difference for every clan
            # on both sides
            clans1_mapped = [{"name": clan.tag, "new_score": new_score, "difference": new_score -  float(clan.score)}
                            for clan, new_score in zip(clans1, new_scores1)]
            clans2_mapped = [{"name": clan.tag, "new_score": new_score, "difference": new_score -  float(clan.score)}
                            for clan, new_score in zip(clans2, new_scores2)]
            return get_response({
                "side1": clans1_mapped,
                "side2": clans2_mapped
            })

        except BadRequest as e:
            return handle_error(f"{e}")
        except ValidationError as e:
            return handle_error(f"validation error: {e}")
        except DoesNotExist as e:
            return handle_error(f"not found: {e}", 404)
        except Exception as e:
            return handle_error(f"something went terribly wrong: {e}", 500)
