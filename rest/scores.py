# rest/scores.py
from flask import request
from flask_restful import Resource
from database.scores import Scores
from mongoengine import Q
from ._common import *


class ScoreApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            score = Scores.objects.get(id=oid)
            return get_response(score)
        except:
            return get_error(f"error getting scores from database, score not found by oid: {oid}")     


class ScoresApi(Resource):
    
    # get all or filtered by clan tag
    def get(self):
        select = request.args.get('select')
        name = request.args.get('name')        

        where = Q(name=name) if name != None else Q()
        fields = select.split(',') if select != None else []
        
        scores = Scores.objects(where).only(*fields)

        return get_response(scores)
