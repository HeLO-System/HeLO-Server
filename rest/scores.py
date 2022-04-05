# rest/scores.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from database.models import Score
from mongoengine import Q
from ._common import *


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
    @jwt_required()
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
    @jwt_required()
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
            select = request.args.get('select')
            clan = request.args.get('clan')        

            where = Q(clan=clan) if clan != None else Q()
            fields = select.split(',') if select != None else []
            
            scores = Score.objects(where).only(*fields)

            return get_response(scores)
        except:
            return handle_error("Error getting scores from database")
        

    # add new scores
    # will be deleted soon
    @jwt_required()
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
        