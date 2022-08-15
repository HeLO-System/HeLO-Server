# rest/routes.py
from rest.clans import ClansApi, ClanApi, ScoreHistoryApi, \
    ConsoleClanApi, ConsoleClansApi, ConsoleScoreHistoryApi
from rest.clans import DiscordRoleApi
from rest.events import EventApi, EventsApi
from rest.matches import MatchApi, MatchesApi, \
    ConsoleMatchApi, ConsoleMatchesApi
from rest.scores import ScoreApi, ScoresApi, \
    ConsoleScoreApi, ConsoleScoresApi
from rest.search import SearchApi
from rest.simulations import SimulationsApi, \
    ConsoleSimulationsApi
from rest.statistics import WinrateApi, ResultTypesApi, PerformanceRatingApi, \
    ConsoleWinrateApi, ConsoleResultTypesApi, ConsolePerformanceRatingApi
from rest.users import SignupApi, LoginApi, UserApi, UsersApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/auth/signup')
    api.add_resource(LoginApi, '/auth/login')
    api.add_resource(UserApi, '/user/<userid>')
    api.add_resource(UsersApi, '/users')
    api.add_resource(ClanApi, '/clan/<oid>')
    api.add_resource(ClansApi, '/clans')
    api.add_resource(ScoreHistoryApi, '/clan/<oid>/score_history')
    api.add_resource(MatchApi, '/match/<match_id>')
    api.add_resource(MatchesApi, '/matches')
    api.add_resource(EventApi, '/event/<oid>')
    api.add_resource(EventsApi, '/events')
    api.add_resource(ScoresApi, '/scores')
    api.add_resource(ScoreApi, '/score/<oid>')
    api.add_resource(SimulationsApi, '/simulations')
    api.add_resource(SearchApi, '/search')
    api.add_resource(WinrateApi, '/statistics/winrate/<oid>')
    api.add_resource(ResultTypesApi, '/statistics/result_types/<oid>')
    api.add_resource(PerformanceRatingApi, '/statistics/pr/<oid>')
    api.add_resource(DiscordRoleApi, '/role_id/<rid>')
    # console
    api.add_resource(ConsoleClanApi, '/console/clan/<oid>')
    api.add_resource(ConsoleClansApi, '/console/clans')
    api.add_resource(ConsoleScoreHistoryApi, '/console/clan/<oid>/score_history')
    api.add_resource(ConsoleMatchApi, '/console/match/<oid>')
    api.add_resource(ConsoleMatchesApi, '/console/matches')
    api.add_resource(ConsoleScoresApi, '/console/scores')
    api.add_resource(ConsoleScoreApi, '/console/score/<oid>')
    api.add_resource(ConsoleSimulationsApi, '/console/simulations')
    api.add_resource(ConsoleWinrateApi, '/console/statistics/winrate/<oid>')
    api.add_resource(ConsoleResultTypesApi, '/console/statistics/result_types/<oid>')
    api.add_resource(ConsolePerformanceRatingApi, '/console/statistics/pr/<oid>')
