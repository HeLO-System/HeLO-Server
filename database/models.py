# database/models.py
from datetime import date

from logic.calculations import get_new_scores, get_coop_scores
from .db import db
from mongoengine.queryset.visitor import Q
from flask_bcrypt import generate_password_hash, check_password_hash


"""
first level class
"""
class Clan(db.Document):
    # e.g. StDb for Stoßtrupp Donnerbalken
    tag = db.StringField(required=True, unique=True)
    # full name
    name = db.StringField()
    # discord icon flag, e.g. :flag_eu:, :flag_de:, ...
    flag = db.StringField()
    # discord invite link to a clan's discord server
    invite = db.StringField()
    # current HeLO Score
    score = db.IntField()
    # number of games
    num_matches = db.IntField()
    # confirmation, reserved ??
    conf = db.StringField()
    # alternative tags, if a clan was renamed, reserved
    alt_tags = db.ListField()
    
    # will be called when the Clan Object is initialized
    # sets the default values for number of matches and score
    def set_default_values(self):
        if self.num_matches is None: self.num_matches = 0
        if self.score is None: self.score = 600

"""
first level class
"""
class Event(db.Document):
    # acronym of the event, like HPL = Hell Let Loose Premier League
    tag = db.StringField(required=True, unique=True)
    # corresponding name to the tag
    name = db.StringField()
    # event emoji, e.g. :hpl:
    emoji = db.StringField()
    # factor for score, e.g. extra sweaty = 1.2
    factor = db.FloatField()
    # discord invite link to the event's discord server
    invite = db.StringField()
    # confirmation, reserved ??
    conf = db.StringField()


"""
first level class
"""
class Match(db.Document):
    # something like "StDb-91.-2022-01-07" what ever
    match_id = db.StringField(required=True, unique=True)
    # unique identifiers (very long number) of the clan -> oid of the clan object in DB
    clans1_ids = db.ListField()
    clans2_ids = db.ListField()
    # clan tag mapped to the number of players they fielded
    # e.g. {"CoRe": 30, "StDb": 20}
    # player distribution is not required, and should be None if not provided
    player_dist1 = db.DictField()
    player_dist2 = db.DictField()
    """
    # unique identifier (very long number) of the clan -> oid of the clan object in DB
    clan1_id     = db.StringField()
    # name of the clan (clan tag)
    clan1        = db.StringField()
    # if clan1 played with another clan
    coop1_id     = db.StringField()
    coop1        = db.StringField()
    clan2_id     = db.StringField()
    clan2        = db.StringField()
    coop2_id     = db.StringField()
    coop2        = db.StringField()
    """
    # allies or axis
    side1        = db.StringField()
    side2        = db.StringField()
    # strong points hold at the end of the game
    caps1        = db.IntField()
    caps2        = db.IntField()
    # number of players on each side (assuming both teams had the same number of players)
    players      = db.IntField()
    map          = db.StringField()
    date         = db.DateTimeField(required=True)
    # how long the game lasted, max is 90 min
    duration     = db.IntField()
    # competitive factor, see HeLO calculations
    factor       = db.FloatField()
    # name of the tournament, of just a training match
    event        = db.StringField()
    # confirmation, very important
    # match must be confirmed from both sides (representatives) in order to
    # take the match into account
    # user id of the user who confirmed the match for clan1
    conf1        = db.StringField()
    # user id of the user who confirmed the match for clan2
    conf2        = db.StringField()
    # flag to check whether corresponding score objects to the match exist or not
    score_posted = db.BooleanField()
    # reserved for admins, necessary to start a recalculate process for this match
    recalculate = db.BooleanField()

    def needs_confirmations(self):
        if (self.conf1 != "" and self.conf1 is not None) and (self.conf2 != "" and self.conf2 is not None):
            # do the calcs then
            return False
        else:
            return True

    def get_clan_objects(self):
        clans1 = [Clan.objects.get(id=oid) for oid in self.clans1_ids]
        clans2 = [Clan.objects.get(id=oid) for oid in self.clans2_ids]
        return clans1, clans2

    def calc_scores(self):
        clans1, clans2 = self.get_clan_objects()
        # hier nihct aus clan, sondern letztes Match object (vor diesem nehmen)
        # z.b. über datum
        scores1, scores2 = [[clan.score for clan in clans1], [clan.score for clan in clans2]]
        # check if it is a coop game or a normal game
        if len(self.clans1_ids) == 1 and len(self.clans2_ids) == 1:
            score1, score2, err = get_new_scores(clans1[0].score, clans2[0].score,
                                                        self.caps1, self.caps2,
                                                        clans1[0].num_matches,
                                                        clans2[0].num_matches,
                                                        self.factor, self.players)
            # for compatibility reasons
            scores1, scores2 = [score1], [score2]
        
        else:
            scores1, scores2, err = get_coop_scores(scores1, scores2, self.caps1,
                                                            self.caps2, self.factor,
                                                            self.player_dist1.items(),
                                                            self.player_dist2.items(),
                                                            self.players)

        self._save_clans_and_scores(clans1, clans2, scores1, scores2)
        self.score_posted = True
        self.save()

        return err

    def _save_clans_and_scores(self, clans1, clans2, scores1, scores2):
        for clan, score in list(zip(clans1, scores1)) + list(zip(clans2, scores2)):
            # get the score object which matches the match_id and the clan (id)
            score_obj = Score.objects(Q(match_id=self.match_id) & Q(clan=str(clan.id)))
            # update or insert if it does not exist
            res = score_obj.update_one(set__score=score, upsert=True, full_result=True)

            # check if it was an insert or update, this is important for the number of matches
            if res.raw_result.get("updatedExisting"):
                clan.update(score=score)
            else:
                clan.update(score=score, inc__num_matches=1)
                clan.reload()
                score_obj.update_one(set__num_matches=clan.num_matches)

    def start_recalculation(self):
        pass

"""
second level class
"""
class User(db.Document):
    # discord id, very long number
    userid = db.StringField(required=True, unique=True)
    # required for login
    pin = db.StringField()
    name = db.StringField()
    # admin or teamrep (team representative)
    role = db.StringField(required=True)
    clan = db.StringField()
    # confirmation of a user (id), reserved ??
    conf = db.StringField()
 
    def hash_password(self):
        self.pin = generate_password_hash(self.pin).decode('utf8')
 
    def check_password(self, pin):
        return check_password_hash(self.pin, pin)


"""
class to store all scores from all clans, this class should be understood as QoL class,
that make things easier in the long run, but should not be considered as "first level class"
Every new score will be stored in a Score object. The maximum amount of score objects
for one clan is the sum of all matches of the clan.
One match results automatically in at least two Score Objects.
"""
class Score(db.Document):
    clan = db.StringField(required=True)
    # number of games, = 31 means it's the score gained from the 31st match
    num_matches = db.IntField(required=True)
    # match id of the match where the score calculation
    # is based on, something like "StDb-91.-2022-01-07"
    match_id = db.StringField(required=True)
    score = db.IntField(required=True)
    # redundant, because with "count" and "clan" we can extract the old score
    # besides when creating the Score object, we don't need to care about
    # double checking whether the score in the corresponding clan object is the same
    # IMPORTANT: clan.score must be updated first!
    # score_before = db.IntField(required=True)

    def __init__(self, clan: str, num_matches: int, match_id: str, score: int, *args, **kwargs):
        super().__init__()
        self.clan = clan
        self.num_matches = num_matches
        self.match_id = match_id
        self.score = score

    @classmethod
    def from_match(cls, match: Match, clan: Clan):
        """Alternative constructor.

        Args:
            match (Match): Match object the calculation is based on
            clan (Clan): Clan that the score belongs to

        Returns:
            Score: the new Score object
        """
        # clan.id is the oid of the Clan object in the DB
        return cls(str(clan.id), clan.num_matches, match.match_id, clan.score)
    
    # def new_from_match(match:Match, clan:Clan):
    #     score = Scores()
    #     score.match = match.match_id
    #     score.clan = str(clan.id)
    #     score.score_before = clan.score
    #     return score

    def get_score_to_num_matches(self, clan_id, num_matches):
        pass
