# rest/matches.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError, DoesNotExist, OperationError
from mongoengine.queryset.visitor import Q
from database.models import Clan, Match, Score
from logic.calculations import get_new_scores
from ._common import *


class MatchApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            match = Match.objects.get(id=oid)
            return get_response(match)
        except:
            return handle_error(f"error getting match from database, match not found by oid: {oid}")
        

    # update match by object id
    @jwt_required()
    def put(self, oid):
        # try:
        #     match = Match.objects.get(id=oid)        
        #     try:
        #         match.update(**request.get_json())
        #         return '', 204
        #     except:
        #         return handle_error(f"error updating match in database: {oid}")
        # except:
        #     return handle_error(f"error updating match in database, match not found by oid: {oid}")
        try:
            match = Match.objects.get(id=oid)
            match.update(**request.get_json())
        except OperationError:
            return handle_error(f"error updating match in database: {oid}")
        except DoesNotExist:
            return handle_error(f"error updating match in database, match not found by oid: {oid}")
        else:
            return '', 204

    # update match by object id
    @jwt_required()
    def delete(self, oid):
        try:
            match = Match.objects.get(id=oid)        
            try:
                match = match.delete()
                return '', 204
            except:
                return handle_error(f"error deleting match in database: {oid}")
        except:
            return handle_error(f"error deleting match in database, match not found by oid: {oid}")
        


class MatchesApi(Resource):
    
    # get all or filtered by match id
    def get(self):
        try:
            select = request.args.get('select')
            match_id = request.args.get('match_id')
            clan_id = request.args.get('clan_id')
            clan1_id = request.args.get('clan1_id')
            coop1_id = request.args.get('coop1_id')
            clan2_id = request.args.get('clan2_id')
            coop2_id = request.args.get('coop2_id')
            conf1 = request.args.get('conf1')
            conf2 = request.args.get('conf2')
            date = request.args.get('date')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')

            fields = select.split(',') if select != None else []
                
            where = Q()
            if match_id != None: where &= Q(match_id=match_id)
            if clan_id != None: where &= (Q(clan1_id=clan_id) | Q(clan2_id=clan_id))
            if clan1_id != None: where &= Q(clan1_id=clan1_id)
            if coop1_id != None: where &= Q(coop1_id=coop1_id)
            if clan2_id != None: where &= Q(clan2_id=clan2_id)
            if coop2_id != None: where &= Q(coop2_id=coop2_id)
            if conf1 != None: where &= Q(conf1=conf1)
            if conf2 != None: where &= Q(conf2=conf2)
            if date != None: where &= Q(date=date)
            if date_from != None: where &= Q(date__gte=date_from)
            if date_to != None: where &= Q(date__lte=date_to)

            matches = Match.objects(where).only(*fields)
                        
            return get_response(matches)
        
        except:
            return handle_error(f'error getting matches')


    # add new match
    # @jwt_required()
    # def post(self):
    #     try:
    #         match = Match(**request.get_json())
    #         try:
    #             # if the match is confirmed and the score has not been posted before, calculate the new scores
    #             if not match.score_posted and not empty(match.conf1) and not empty(match.conf2):
    #                 # mongoengine does not support transactions!!! :(
                    
    #                 # get clans/coop partners by id or by tag
    #                 clan1 = Clan.objects(id=match.clan1_id).first() if match.clan1_id != None else Clan.objects(tag=match.clan1).first()
                    
    #                 if match.coop1_id != None:
    #                     coop1 = Clan.objects(id=match.coop1_id).first() if match.coop1_id != None else Clan.objects(tag=match.coop1).first()
                        
    #                 clan2 = Clan.objects(id=match.clan2_id).first() if match.clan2_id != None else Clan.objects(tag=match.clan2).first()
                    
    #                 if match.coop2_id != None:
    #                     coop2 = Clan.objects(id=match.coop2_id).first() if match.coop2_id != None else Clan.objects(tag=match.coop2).first()
                    
    #                 clan1.init()
    #                 clan2.init()
                    
    #                 # get initial score for clans/coop partners
    #                 score_clan1 = Scores.new_from_match(match, clan1)
    #                 score_clan2 = Scores.new_from_match(match, clan2)                    
    #                 # calculate new values
    #                 clan1.matches += 1
    #                 clan2.matches += 1
    #                 clan1.score, clan2.score, error = get_new_scores(score1=clan1.score, score2=clan2.score, caps1=match.caps1, caps2=match.caps2, matches1=clan1.matches, matches2=clan2.matches, c=match.factor, number_of_players=match.players)
    #                 # update initial scores with new values
    #                 score_clan1.score = clan1.score
    #                 score_clan1.count = clan1.matches
    #                 score_clan2.score = clan2.score
    #                 score_clan2.count = clan2.matches
    #                 if error != None:
    #                     logging.error(f"error calculating scores: {error}")
    #                 else:
    #                     # save data to db
    #                     clan1.save()
    #                     clan2.save()
    #                     score_clan1.save()
    #                     score_clan2.save()
    #                     match.score_posted = True
                
    #             # save match data           
    #             match = match.save()
    #             return get_response({ "match_id": match.match_id })
    #         except NotUniqueError:
    #             return handle_error(f"match already exists in database: {match.match_id}")
    #         except:
    #             return handle_error(f"error creating match in database: {match.match_id}")
    #     except:
    #         return handle_error(f'error creating match in database')

    # add new match
    @jwt_required()
    def post(self):
        try:
            match = Match(**request.get_json())
            match = match.save()
            need_conf = match.needs_confirmations()
        except:
            return handle_error(f'error creating match in database')
        else:
            return get_response({ "match_id": match.match_id, "confirmed": not need_conf })
