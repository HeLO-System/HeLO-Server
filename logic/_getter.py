from mongoengine.queryset.visitor import Q
from mongoengine.errors import DoesNotExist

from models.clan import Clan
from models.match import Match
from models.score import Score

def get_clan_objects(match: Match):
    clans1 = [Clan.objects.get(id=oid) for oid in match.clans1_ids]
    clans2 = [Clan.objects.get(id=oid) for oid in match.clans2_ids]
    return clans1, clans2


def get_by_clan_id(match: Match, clan_id: str):
    """Returns a Score object that matches a specific match_id and clan_id.

    Args:
        match (Match): Match object
        clan_id (str): id of a clan

    Returns:
        Score: Score matching the query
    """
    try:
        return Score.objects.get(Q(match_id=match.match_id) & Q(clan=clan_id))
    # if the match haven't been confirmed, there won't be a matching Score object
    # in this case, find the last (before the given one) match by date
    except DoesNotExist:
        matches = []
        for m in Match.objects(Q(date__lte=match.date) & (Q(clans1_ids__in=[clan_id]) | (Q(clans2_ids__in=[clan_id])))):
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
            return get_by_clan_id(matches[0], clan_id)
        except IndexError:
            return Score(clan_id, 0, "DefaultScore", 600)


def get_by_num_matches(clan_id: str, num_matches: int):
    """Returns a Score object that matches a specific clan_id and number of matches.

    Args:
        clan_id (str): id of a clan
        num_matches (int): number of matches

    Returns:
        Score: Score matching the query
    """
    try:
        return Score.objects.get(Q(clan=clan_id) & Q(num_matches=num_matches))
    except DoesNotExist:
        return Score(clan_id, 0, "DefaultScore", 600)
