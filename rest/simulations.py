# rest/matches.py
from flask import request
from flask_restful import Resource
from logic.calculations import *
from database.models import Clan, Score
from ._common import *

# helper for getting data for the clan name in the given input parameter
def get_score_for_arg(arg):   
    clan : Clan = Clan.objects(clan=request.args.get(arg))
    scores = Score.objects(clan=clan.id).order_by('-count').only("score").first()
    if scores == None: 
        return clan.tag, None, f"Error retrieving score for clan: {clan.tag}"
        
    return clan.tag, scores.score, None


class SimulationsApi(Resource):
    
    def get(self):
        try:
            if len(set(request.args) & {"clan1", "clan2"}) != 2: 
                return handle_error(f'Must provide parameters clan1, clan2 and optional result parameters caps1, caps2!')
            
            # get selection fields
            fields = request.args.get('select')            
            if fields != None: fields = fields.split(",")
            
            # get scores
            clan1, score1, error1 = get_score_for_arg('clan1')
            clan2, score2, error2 = get_score_for_arg('clan2')

            if error1 != None: return get_response({ "error": error1 })
            if error2 != None: return get_response({ "error": error2 })

            body = { "clan1": clan1, "clan2": clan2, "score1": score1, "score2": score2 }
            
            # get probs
            if fields == None or len(set(fields) & {"prob1", "prob2"}) > 0:
                prob1, prob2 = get_win_prob(score1, score2)
                
                body["prob1"] = prob1
                body["prob2"] = prob2
            
            # get new scores and deltas
            if fields == None or len(set(fields) & {"score1_new", "score2_new", "delta1", "delta2"}) > 0:
                caps1 = request.args.get('caps1')
                caps2 = request.args.get('caps2')
                            
                if caps1 != None and caps2 != None:
                    body["caps1"] = caps1 = int(caps1)
                    body["caps2"] = caps2 = int(caps2)
                    
                    score1_new, score2_new, error = get_new_scores(score1, score2, caps1, caps2)
                    
                    if error == None:            
                        body["score1_new"] = score1_new
                        body["score2_new"] = score2_new
                        body["delta1"] = score1 - score1_new
                        body["delta2"] = score2 - score2_new
            
            # only keep values that have been selected
            if fields != None:
                body = { key: body[key] for key in body if key in fields }
            
            return get_response(body)
        except:
            return handle_error("Error retrieving match data")
        
