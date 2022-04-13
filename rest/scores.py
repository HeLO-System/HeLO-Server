# rest/scores.py
from flask import request
from flask_restful import Resource
from mongoengine import Q
from mongoengine.errors import LookUpError

from models.score import Score
from ._common import get_response, handle_error, empty, admin_required


class ScoreApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            score = Score.objects.get(id=oid)
            return get_response(score)
        except:
            return handle_error(f"Error getting scores from database, score not found by oid: {oid}")     


    # update scores by object id
    # will be deleted soon
    @admin_required()
    def put(self, oid):
        try:
            scores = Score.objects.get(id=oid)        
            try:
                scores.update(**request.get_json())
                return '', 204
            except:
                return handle_error(f"error updating scores in database: {oid}")
        except:
            return handle_error(f"error updating scores in database, scores not found by oid: {oid}")

    # update scores by object id
    @admin_required()
    def delete(self, oid):
        try:
            scores = Score.objects.get(id=oid)        
            try:
                scores = scores.delete()
                return '', 204
            except:
                return handle_error(f"error deleting scores in database: {oid}")
        except:
            return handle_error(f"error deleting scores in database, scores not found by oid: {oid}")
        



class ScoresApi(Resource):
    
    # get all or filtered by clan tag
    def get(self):
        try:
            select = request.args.get("select")
            clan = request.args.get("clan_id")
            match_id = request.args.get("match_id")
            num = request.args.get("num")
            num_from = request.args.get("num_from")
            num_to = request.args.get("num_to")
            score = request.args.get("score")
            score_from = request.args.get("score_from")
            score_to = request.args.get("score_to")

            fields = select.split(',') if select is not None else []

            filter = Q()

            if not empty(clan): filter &= Q(clan=clan)
            if not empty(match_id): filter &= Q(match_id__icontains=match_id)
            if not empty(num): filter &= Q(num_matches=num)
            if not empty(num_from): filter &= Q(num_matches__gte=num_from)
            if not empty(num_to): filter &= Q(num_matches__lte=num_from)
            if not empty(score): filter &= Q(score=score)
            if not empty(score_from): filter &= Q(score__gte=score_from)
            if not empty(score_to): filter &= Q(score__lte=score_from)
            
            total = Score.objects(filter).only(*fields).count()
            scores = Score.objects(filter).only(*fields)

            res = {
                "total": total,
                "items": scores.to_json_serializable()
            }

            return get_response(res)

        except LookUpError:
            return {"error": f"cannot resolve field 'select={select}'"}, 400

        except:
            return handle_error("Error getting scores from database")
        

    # add new scores
    # will be deleted soon
    @admin_required()
    def post(self):
        try:
            score = Score(**request.get_json())
            try: 
                score = score.save()
                return get_response({ "id": score.id })
            except:
                return handle_error(f"error creating scores in database: {score.id}")
        except:
            return handle_error(f'error creating scores in database')
        