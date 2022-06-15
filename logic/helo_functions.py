# logic/helo_functions.py
import math
import numpy as np


def get_win_prob(score1, score2):
    """Calculates the probability of winning for the better team.

    Args:
        score1 (int): HeLO score of one team
        score2 (int): HeLO score of the other team

    Returns:
        float, float: probability for better ranked team (score1)
                      and worse ranked team (score2) between [0, 1]
    """
    assert score1 > 0 and score2 > 0
    # difference of the HeLO scores, make sure not to exceed the maximum difference of 400
    diff = min(400, abs(score1 - score2))
    # round the probability to three decimal places
    prob = round(0.5*(math.erf(diff/400) + 1), 3)
    # prob is the winning probability for the better score, return probabilities accordingly
    if score1 > score2:
        return prob, round(1 - prob, 3)
    else:
        return round(1 - prob, 3), prob


def get_new_scores(score1, score2, caps1, caps2, matches1=0, matches2=0, c=2, number_of_players=50):
    """Calculates the new HeLO score based on a given game score.

    Args:
        score1 (int): HeLO score of the first team
        score2 (int): HeLO score of the second team
        caps1 (str): strong points captured by the first team at the end of the match
        caps2 (str): strong points captured by the second team at the end of the match
        matches1 (int, optional): number of games played (team 1). Defaults to 0.
        matches2 (int, optional): number of games played (team 2). Defaults to 0.
        c (int, optional): competitive factor, possible values = {0.5, 0.8, 1, 1.2}. Defaults to 1.
        number_of_players (int, optional): Number of players played in the game per team. Defaults to 50.

    Returns:
        int, int, str: new HeLO score for team 1 and team 2, possible error
    """
    try:
        # determine the "amount factor" by the number of games played
        a1 = 20 if matches1 is not None and matches1 > 30 else 40
        a2 = 20 if matches2 is not None and matches2 > 30 else 40
        # calculate the probabilities for the teams
        prob1, prob2 = get_win_prob(score1, score2)
        # check if points don't exceed maximum points, which are possible in HLL
        assert 4 < caps1 + caps2 <= 5
        # calulate the new HeLO scores
        score1_new = score1 + a1 * float(c) * (math.log(number_of_players/50, a1) + 1) * float(caps1 / 5 - prob1)
        score2_new = score2 + a2 * float(c) * (math.log(number_of_players/50, a2) + 1) * float(caps2 / 5 - prob2)
        return round(score1_new), round(score2_new), None
    except AssertionError:
        return None, None, "Sum of points in score must be between 4 and 5"


def get_coop_scores(clan_scores1: list, clan_scores2: list, caps1: int, caps2: int, c: int = 2,
                    player_dist1: list = None, player_dist2: list = None, num_players: int = 50,
                    num_matches1: list = None, num_matches2: list = None):
    """Calculates the scores for games with more than one clan on one (or both) side(s).
    If a player distribution is given, the score will be calculated based on a weighted
    average. Otherwise a normal average will be calculated.

    Args:
        clan_scores1 (list): list of scores of the clans in the cooperation
        clan_scores2 (list): list of scores of the clans in the cooperation on the other side
        caps1 (int): strongpoints held by clans1 at the end of the game
        caps2 (int): strongpoints held by clans2 at the end of the game
        c (int, optional): competitive factor, possible values = {0.5, 0.8, 1, 1.2}. Defaults to 1.
        player_dist1 (list, optional): player distributions of the participating clans1.
                                        Defaults to None.
        player_dist2 (list, optional): player distributions of the participating clans2.
                                        Defaults to None.
        num_players (list, optional): total number of players, only necessary if no player
                                        distribution was given
        num_matches1 (list, optional): list of number of matches for side 1
        num_matches2 (list, optional): list of number of matches for side 2

    Returns:
        list, list: list of the new HeLO scores for every team (coop1, coop2)
    """
    # note: amount factor (a) will be ignored here, default is 40
    # otherwise, these kind of games won't generate a significant score
    # TODO: known issue: a coop game is also a game where only one clan plays against
    # two or more clans, therefore the clan playing alone will be weighted with a = 40
    # regardless of its number of games
    a1, a2 = 40, 40
    # temporary fix: if there is a clan in the cooperation with > 30 games, take 20
    if num_matches1 is not None:
        a1 = min([40 if num <= 30 else 20 for num in num_matches1])
    if num_matches2 is not None:
        a2 = min([40 if num <= 30 else 20 for num in num_matches2])

    # performs normal average
    weights1 = np.ones(len(clan_scores1)) / len(clan_scores1)
    weights2 = np.ones(len(clan_scores2)) / len(clan_scores2)

    # convert player distributions to numpy arrays and normalize
    if player_dist1:
        # performs weighted average later
        weights1 = np.array(player_dist1) / sum(player_dist1)
        num_players = sum(player_dist1)
    if player_dist2:
        # performs weighted average later
        weights2 = np.array(player_dist2) / sum(player_dist2)
        num_players = sum(player_dist2)

    # calculate the (weighted) average score of the cooperations
    avg1 = np.average(clan_scores1, weights=weights1)
    avg2 = np.average(clan_scores2, weights=weights2)

    score1, score2, err = get_new_scores(avg1, avg2, caps1, caps2,
                                        c=c, number_of_players=num_players,
                                        matches1=a1, matches2=a2)
    if err is not None: return None, None, err
    gain1, gain2 = score1 - avg1, score2 - avg2

    # share the gain depending on the player distribution
    # if there is no player distribution, share equally
    # cs = clan score, part = partial share according to the distribution
    clan_scores1 = [round(cs + part * gain1) for cs, part in zip(clan_scores1, weights1)]
    clan_scores2 = [round(cs + part * gain2) for cs, part in zip(clan_scores2, weights2)]

    return clan_scores1, clan_scores2, err
