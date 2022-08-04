"""
Recalculations for the Scores
"""

from models.match import Match
from logic.calculations import calc_scores
from ._getter import get_clan_objects, get_by_clan_id, get_by_num_matches


def start_recalculation(match, console=False):
        clans1, clans2 = get_clan_objects(match)
        scores1, num_matches1 = zip(*[_get_score_and_num_matches(match, clan, console) for clan in clans1])
        scores2, num_matches2 = zip(*[_get_score_and_num_matches(match, clan, console) for clan in clans2])
        print(match.match_id)
        # calculate new scores
        err = calc_scores(match, scores1, num_matches1, scores2, num_matches2, recalculate=True)

        # get all updated teams
        updated_teams = clans1 + clans2

        # get all matches where date is greater
        # note, that some teams play multiple games on one day
        # that's why we use gte = greater than or equal to
        # but this also delivers the same match as match ...
        all_matches = []
        for m in Match.objects(date__gte=match.date):
            # ... just discard it
            if m.match_id == match.match_id:
                continue
            else:
                all_matches.append(m)

        # sort all matches by ascending date
        all_matches.sort(key=lambda x: x.date)
        for m in all_matches:
            clans1, clans2 = get_clan_objects(m)
            updated_teams.extend(clans1 + clans2)
            # makes searching more efficient if there are no dublicates
            updated_teams = list(set(updated_teams))
            # get the scores and number of matches for the recalculation
            # TODO: make this more efficient by storing all scores and num_matches
            # then we do not have to make database calls
            scores1, num_matches1 = zip(*[_get_score_and_num_matches(m, clan, console) for clan in clans1])
            scores2, num_matches2 = zip(*[_get_score_and_num_matches(m, clan, console) for clan in clans2])
            err = calc_scores(m, scores1, num_matches1, scores2, num_matches2, recalculate=True, console=console)
            print(err, "match:", m.match_id)

        match.recalculate = False
        match.save()

def _get_score_and_num_matches(match, clan, console=False):
    score_obj = get_by_clan_id(match, str(clan.id))
    num = score_obj.num_matches
    # if there does not exist a score object, because the match was added afterwards,
    # then we do not have to go back another step / take the score object before that
    # otherwise we need to use the old score (one match before the given match)
    if match.score_posted:
        score_obj = get_by_num_matches(str(clan.id), num - 1, console)
    score = score_obj.score
    return score, num
