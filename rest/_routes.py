# rest/routes.py
from rest.simulations import SimulationsApi
from .auth import SignupApi, LoginApi, UserApi
from .clans import ClansApi, ClanApi
from .scores import ScoreApi, ScoresApi
from .matches import MatchApi, MatchesApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/auth/signup')
    api.add_resource(LoginApi, '/auth/login')
    api.add_resource(UserApi, '/user/<userid>')
    api.add_resource(ClanApi, '/clan/<oid>')
    api.add_resource(ClansApi, '/clans')
    api.add_resource(MatchApi, '/match/<oid>')    
    api.add_resource(MatchesApi, '/matches')    
    api.add_resource(ScoresApi, '/scores')
    api.add_resource(ScoreApi, '/score/<oid>')
    api.add_resource(SimulationsApi, '/simulations')
