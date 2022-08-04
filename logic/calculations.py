"""
Score Calculation and Database Interactions
"""

from mongoengine.queryset.visitor import Q
from datetime import datetime

from logic.helo_functions import get_new_scores, get_coop_scores
from models.match import Match
from models.score import Score
from models.console.console_match import ConsoleMatch
from models.console.console_score import ConsoleScore
from ._getter import get_clan_objects


def calc_scores(match, scores1=None, num_matches1=None, scores2=None, num_matches2=None,
                recalculate=False, console=False):
        clans1, clans2 = get_clan_objects(match)
        # hier nihct aus clan, sondern letztes Match object (vor diesem nehmen)
        # z.b. über datum
        if scores1 is None and num_matches1 is None and scores2 is None and num_matches2 is None:
            scores1, scores2 = [[clan.score for clan in clans1], [clan.score for clan in clans2]]
            num_matches1, num_matches2 = [[clan.num_matches for clan in clans1], [clan.num_matches for clan in clans2]]

        if set(clans1) & set(clans2):
            # a clan cannot play against itself
            raise RuntimeError("A clan cannot play against itself.")

        if not console:
            # check if it is a coop game or a normal game
            if len(match.clans1_ids) == 1 and len(match.clans2_ids) == 1:
                score1, score2, err = get_new_scores(scores1[0], scores2[0],
                                                            match.caps1, match.caps2,
                                                            num_matches1[0],
                                                            num_matches2[0],
                                                            match.factor, match.players)
                # for compatibility reasons
                scores1, scores2 = [score1], [score2]
            
            else:
                scores1, scores2, err = get_coop_scores(scores1, scores2, match.caps1,
                                                                match.caps2, match.factor,
                                                                match.player_dist1,
                                                                match.player_dist2,
                                                                match.players,
                                                                num_matches1=num_matches1,
                                                                num_matches2=num_matches2)
        
        else:
            # TODO: console computations
            pass

        _save_clans_and_scores(match, clans1, clans2, scores1, scores2, num_matches1,
                                num_matches2, recalculate=recalculate, console=console)
        match.score_posted = True
        match.save()

        return err


def _save_clans_and_scores(match, clans1, clans2, scores1, scores2, num_matches1,
                            num_matches2, recalculate=False, console=False):
        if not console:
            score_obj = Score
            match_obj = Match
        else:
            score_obj = ConsoleScore
            match_obj = ConsoleMatch
        for clan, score, num_matches in list(zip(clans1, scores1, num_matches1)) + list(zip(clans2, scores2, num_matches2)):
            # get the score object which matches the match_id and the clan (id)
            score_queryset = score_obj.objects(Q(match_id=match.match_id) & Q(clan=str(clan.id)))
            # update or insert if it does not exist
            res = score_queryset.update_one(set__score=score, upsert=True, full_result=True)

            # check if it was an insert or update, this is important for the number of matches
            if res.raw_result.get("updatedExisting"):
                clan.update(score=score, last_updated=datetime.now())

            else:
                # TODO: BUG, multiple recalculations lead to a higher num_matches
                clan.update(score=score, last_updated=datetime.now(), inc__num_matches=1)
                # set creation time of score object only if the score is new
                # why is this necessary? update_one does not check whether the given fields match the required formats
                # TODO: should be equal to the date of match
                # score_queryset.update_one(set___created_at=datetime.now())
                score_queryset.update_one(set___created_at=match.date)

                if recalculate:
                    # +1, because the num_matches is before the score has been calculated
                    # we need to replace the matching score object's num_matches after the calculation
                    num = num_matches + 1
                    # update all scores after the match
                    # TODO: make this all more efficient
                    # all matches after the match that is new (including the match itmatch, because of 'gte' but ...)
                    matches_after = match_obj.objects(Q(date__gte=match.date))
                    # all scores after the match that is new
                    scores_after = [score_obj.objects(Q(clan=str(clan.id)) & Q(match_id=match.match_id)) for match in matches_after]
                    # update every match that comes after the new match
                    for score in scores_after:
                        score.update_one(inc__num_matches=1)
                    # ... it does not matter, because we are setting the num_matches to the correct value here
                    score_queryset.update_one(set__num_matches=num)

                else:
                    clan.reload()
                    # TODO: BUG, if there is no Score object and we recalculate, the num_matches is set
                    # to the clan's num_matches, even if this isn't the true num_matches
                    # edit: bug fixed for the moment with 'if recalculate'
                    score_queryset.update_one(set__num_matches=clan.num_matches)
