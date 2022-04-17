# rest/routes.py
from rest.events import EventApi, EventsApi
from rest.search import SearchApi
from rest.simulations import SimulationsApi
from rest.users import SignupApi, LoginApi, UserApi, UsersApi
from rest.clans import ClansApi, ClanApi, ScoreHistoryApi
from rest.scores import ScoreApi, ScoresApi
from rest.matches import MatchApi, MatchesApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/auth/signup')
    api.add_resource(LoginApi, '/auth/login')
    api.add_resource(UserApi, '/user/<userid>')
    api.add_resource(UsersApi, '/users')
    api.add_resource(ClanApi, '/clan/<oid>')
    api.add_resource(ClansApi, '/clans')
    api.add_resource(ScoreHistoryApi, '/clan/<oid>/score_history')
    api.add_resource(MatchApi, '/match/<oid>')  # oid is the unique identifier from MongoDB, "_id"
    api.add_resource(MatchesApi, '/matches')    
    api.add_resource(EventApi, '/event/<oid>')
    api.add_resource(EventsApi, '/events')
    api.add_resource(ScoresApi, '/scores')
    api.add_resource(ScoreApi, '/score/<oid>')
    api.add_resource(SimulationsApi, '/simulations')
    api.add_resource(SearchApi, '/search')
