# rest/scores.py
from flask import request
from flask_restful import Resource
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


class ScoresApi(Resource):
    
    # get all or filtered by clan tag
    def get(self):
        try:
            select = request.args.get('select')
            name = request.args.get('name')        

            where = Q(name=name) if name != None else Q()
            fields = select.split(',') if select != None else []
            
            scores = Score.objects(where).only(*fields)

            return get_response(scores)
        except:
            return handle_error("Error getting scores from database")