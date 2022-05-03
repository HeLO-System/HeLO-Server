# rest/matches.py
from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from logic.helo_functions import get_win_prob, get_new_scores, get_coop_scores
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

            # coop game
            if len(clans1) > 1 or len(clans2) > 1:
                # TODO: add factor and number of players via queries
                new_scores1, new_scores2, err = get_coop_scores(
                    clan_scores1=[clan.score for clan in clans1],
                    clan_scores2=[clan.score for clan in clans2],
                    caps1=request.get_json().get("caps1"),
                    caps2=request.get_json().get("caps2"),
                    player_dist1=request.get_json().get("player_dist1"),
                    player_dist2=request.get_json().get("player_dist2")
                    )
            
            # no coop game
            else:
                # TODO: add factor and number of players via queries
                new_scores1, new_scores2, err = get_new_scores(
                    score1=clans1[0].score,
                    score2=clans2[0].score,
                    caps1=request.get_json().get("caps1"),
                    caps2=request.get_json().get("caps2"),
                    matches1=clans1[0].num_matches,
                    matches2=clans2[0].num_matches,
                    )
                # TODO: ugly, make this better
                new_scores1, new_scores2 = [new_scores1], [new_scores2]

            clans1_mapped = {clan.tag : {"new_score": new_score, "difference": new_score -  clan.score}
                            for clan, new_score in zip(clans1, new_scores1)}
            clans2_mapped = {clan.tag : {"new_score": new_score, "difference": new_score -  clan.score}
                            for clan, new_score in zip(clans2, new_scores2)}
            return get_response({
                "side1": clans1_mapped,
                "side2": clans2_mapped
            })

        except BadRequest as e:
            return handle_error(f"terminated with error: {e}")
        except Exception as e:
            return handle_error(f"something went terribly wrong: {e}")

    # def get(self):
    #     try:
    #         if len(set(request.args) & {"clan1", "clan2"}) != 2: 
    #             return handle_error(f'Must provide parameters clan1, clan2 and optional result parameters caps1, caps2!')
            
    #         # get selection fields
    #         fields = request.args.get('select')            
    #         if fields != None: fields = fields.split(",")
            
    #         # get scores
    #         clan1, score1, error1 = get_score_for_arg('clan1')
    #         clan2, score2, error2 = get_score_for_arg('clan2')

    #         if error1 != None: return get_response({ "error": error1 })
    #         if error2 != None: return get_response({ "error": error2 })

    #         body = { "clan1": clan1, "clan2": clan2, "score1": score1, "score2": score2 }
            
    #         # get probs
    #         if fields == None or len(set(fields) & {"prob1", "prob2"}) > 0:
    #             prob1, prob2 = get_win_prob(score1, score2)
                
    #             body["prob1"] = prob1
    #             body["prob2"] = prob2
            
    #         # get new scores and deltas
    #         if fields == None or len(set(fields) & {"score1_new", "score2_new", "delta1", "delta2"}) > 0:
    #             caps1 = request.args.get('caps1')
    #             caps2 = request.args.get('caps2')
                            
    #             if caps1 != None and caps2 != None:
    #                 body["caps1"] = caps1 = int(caps1)
    #                 body["caps2"] = caps2 = int(caps2)
                    
    #                 score1_new, score2_new, error = get_new_scores(score1, score2, caps1, caps2)
                    
    #                 if error == None:            
    #                     body["score1_new"] = score1_new
    #                     body["score2_new"] = score2_new
    #                     body["delta1"] = score1 - score1_new
    #                     body["delta2"] = score2 - score2_new
            
    #         # only keep values that have been selected
    #         if fields != None:
    #             body = { key: body[key] for key in body if key in fields }
            
    #         return get_response(body)
    #     except:
    #         return handle_error("Error retrieving match data")
        
