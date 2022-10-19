"""
Getter functions to retrieve certain information from the database
"""

from mongoengine.queryset.visitor import Q
from mongoengine.errors import DoesNotExist

from models.clan import Clan
from models.match import Match
from models.score import Score
from models.console.console_clan import ConsoleClan
from models.console.console_match import ConsoleMatch
from models.console.console_score import ConsoleScore

def get_clan_objects(match):
    if isinstance(match, Match):
        clan_obj = Clan
    else:
        clan_obj = ConsoleClan
    clans1 = [clan_obj.objects.get(id=oid) for oid in match.clans1_ids]
    clans2 = [clan_obj.objects.get(id=oid) for oid in match.clans2_ids]
    return clans1, clans2


def get_by_clan_id(match, clan_id: str):
    """Returns a Score object that matches a specific match_id and clan_id.

    Args:
        match (Match): Match object
        clan_id (str): id of a clan

    Returns:
        Score: Score matching the query
    """
    if isinstance(match, Match):
        score_obj = Score
        match_obj = Match
        console = False
    else:
        score_obj = ConsoleScore
        match_obj = ConsoleMatch
        console = True
    try:
        return score_obj.objects.get(Q(match_id=match.match_id) & Q(clan=clan_id))
    # if the match haven't been confirmed, there won't be a matching Score object
    # in this case, find the last (before the given one) match by date
    except DoesNotExist:
        matches = []
        for m in match_obj.objects(Q(date__lte=match.date) & (Q(clans1_ids__in=[clan_id]) | (Q(clans2_ids__in=[clan_id])))):
            # discard the match itself, but we need 'lte' in case there is
            # another match on this day
            if m.match_id == match.match_id:
                continue
            else:
                matches.append(m)
        # sort matches, latest (before the current) first
        # e.g. 2022-03-03 -> 2022-03-02 -> ...
        matches.sort(key=lambda x: x.date, reverse=True)
        # if there is no match at all, return default score object with 600
        try:
            # TODO: BUG: match on same date will result in an endless loop, because
            # if both matches have no score object in DB, they will return each other over
            # and over again!!
            return get_by_clan_id(matches[0], clan_id)
        except IndexError:
            return score_obj(clan_id, 0, "DefaultScore", 600 if not console else 1000)


def get_by_num_matches(clan_id: str, num_matches: int, console=False):
    """Returns a Score object that matches a specific clan_id and number of matches.

    Args:
        clan_id (str): id of a clan
        num_matches (int): number of matches

    Returns:
        Score: Score matching the query
    """
    if not console:
        score_obj = Score
    else:
        score_obj = ConsoleScore
    try:
        return score_obj.objects.get(Q(clan=clan_id) & Q(num_matches=num_matches))
    except DoesNotExist:
        return score_obj(clan_id, 0, "DefaultScore", 600 if not console else 1000)


def get_model(t: str, console=False):
    """Returns the database model for a specific type keyword.

    Args:
        t (str): type, allowed values: 'clan', 'match', 'score'

    Raises:
        ValueError: not allowed value used

    Returns:
        cls: model class from the database
    """
    if not console:
        if t == "clan":
            return Clan
        elif t == "match":
            return Match
        elif t == "score":
            return Score
        else:
            raise ValueError
    else:
        if t == "clan":
            return ConsoleClan
        elif t == "match":
            return ConsoleMatch
        elif t == "score":
            return ConsoleScore
        else:
            raise ValueError
