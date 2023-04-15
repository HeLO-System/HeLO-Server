# rest/routes.py
from rest.clans import (
    ClansApi,
    ClanApi,
    ScoreHistoryApi,
    ConsoleClanApi,
    ConsoleClansApi,
    ConsoleScoreHistoryApi,
)
from rest.clans import DiscordRoleApi
from rest.events import EventApi, EventsApi
from rest.matches import (
    MatchApi,
    MatchesApi,
    ConsoleMatchApi,
    ConsoleMatchesApi,
    MatchesNotificationApi,
)
from rest.scores import ScoreApi, ScoresApi, ConsoleScoreApi, ConsoleScoresApi
from rest.search import SearchApi
from rest.simulations import SimulationsApi, ConsoleSimulationsApi
from rest.statistics import (
    WinrateApi,
    ResultTypesApi,
    PerformanceRatingApi,
    ConsoleWinrateApi,
    ConsoleResultTypesApi,
    ConsolePerformanceRatingApi,
)
from rest.users import DiscordLogin, DiscordCallback, LegacyLoginApi


def initialize_routes(api, discord):
    # Shared
    # Auth
    api.add_resource(
        DiscordLogin,
        "/auth/discord/login",
        "/console/auth/discord/login",
        resource_class_kwargs={"discord": discord},
    )
    api.add_resource(
        DiscordCallback,
        "/auth/discord/callback",
        "/console/auth/discord/callback",
        resource_class_kwargs={"discord": discord},
    )
    api.add_resource(LegacyLoginApi, "/auth/login", "/console/auth/login")

    # Matches
    api.add_resource(
        MatchesNotificationApi,
        "/matches-notifications",
        "/console/matches-notifications",
    )

    # Search
    api.add_resource(SearchApi, "/search", "/console/search")

    # PC
    # Clans
    api.add_resource(ClanApi, "/clan/<oid>")
    api.add_resource(ClansApi, "/clans")
    api.add_resource(ScoreHistoryApi, "/clan/<oid>/score_history")

    # Matches
    api.add_resource(MatchApi, "/match/<match_id>")
    api.add_resource(MatchesApi, "/matches")

    # Events
    api.add_resource(EventApi, "/event/<oid>")
    api.add_resource(EventsApi, "/events")

    # Scores
    api.add_resource(ScoresApi, "/scores")
    api.add_resource(ScoreApi, "/score/<oid>")

    # Simulations
    api.add_resource(SimulationsApi, "/simulations")

    # Statistics
    api.add_resource(WinrateApi, "/statistics/winrate/<oid>")
    api.add_resource(ResultTypesApi, "/statistics/result_types/<oid>")
    api.add_resource(PerformanceRatingApi, "/statistics/pr/<oid>")

    # console
    # Clans
    api.add_resource(ConsoleClanApi, "/console/clan/<unique_identifier>") # unique identifier can be Object ID or clan tag
    api.add_resource(ConsoleClansApi, "/console/clans")
    api.add_resource(ConsoleScoreHistoryApi, "/console/clan/<oid>/score_history")

    # Matches
    api.add_resource(ConsoleMatchApi, "/console/match/<match_id>")
    api.add_resource(ConsoleMatchesApi, "/console/matches")

    # Events

    # Scores
    api.add_resource(ConsoleScoresApi, "/console/scores")
    api.add_resource(ConsoleScoreApi, "/console/score/<oid>")

    # Simulations
    api.add_resource(ConsoleSimulationsApi, "/console/simulations")

    # Statistics
    api.add_resource(ConsoleWinrateApi, "/console/statistics/winrate/<oid>")
    api.add_resource(ConsoleResultTypesApi, "/console/statistics/result_types/<oid>")
    api.add_resource(ConsolePerformanceRatingApi, "/console/statistics/pr/<oid>")
