# rest/matches.py
from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from mongoengine.errors import ValidationError, DoesNotExist

from logic.helo_functions import get_new_scores, get_coop_scores
from models.clan import Clan
from schemas.request_schemas import SimulationsSchema
from ._common import get_response, handle_error, validate_schema

# helper for getting data for the clan name in the given input parameter
# def get_score_for_arg(arg):   
#     clan : Clan = Clan.objects(clan=request.args.get(arg))
#     scores = Score.objects(clan=clan.id).order_by('-count').only("score").first()
#     if scores == None: 
#         return clan.tag, None, f"Error retrieving score for clan: {clan.tag}"
        
#     return clan.tag, scores.score, None


class SimulationsApi(Resource):
    
    def get(self):
        try:
            validate_schema(SimulationsSchema(), request.get_json())

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
                    player_dist1=request.get_json().get("player_dist1"),
                    player_dist2=request.get_json().get("player_dist2"),
                    c=c,
                    num_players=players
                    )
            
            # no coop game
            else:
                new_scores1, new_scores2, err = get_new_scores(
                    score1=clans1[0].score,
                    score2=clans2[0].score,
                    caps1=request.get_json().get("caps1"),
                    caps2=request.get_json().get("caps2"),
                    matches1=clans1[0].num_matches,
                    matches2=clans2[0].num_matches,
                    c=c,
                    number_of_players=players
                    )
                # TODO: ugly, make this better
                new_scores1, new_scores2 = [new_scores1], [new_scores2]

            if err is not None: raise BadRequest("calculation failed due to logical reasons, please check your input")

            clans1_mapped = {clan.tag : {"new_score": new_score, "difference": new_score -  clan.score}
                            for clan, new_score in zip(clans1, new_scores1)}
            clans2_mapped = {clan.tag : {"new_score": new_score, "difference": new_score -  clan.score}
                            for clan, new_score in zip(clans2, new_scores2)}
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
