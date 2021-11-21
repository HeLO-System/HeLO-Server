# rest/routes.py
from .scores import ScoreApi, ScoresApi
from .matches import MatchesApi


def initialize_routes(api):
    api.add_resource(ScoresApi, '/scores')
    api.add_resource(ScoreApi, '/score')
    api.add_resource(MatchesApi, '/matches')    
