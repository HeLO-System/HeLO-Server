# rest/matches.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import DoesNotExist, OperationError
from mongoengine.queryset.visitor import Q

from models.match import Match
from logic.calculations import calc_scores
from logic.recalculations import start_recalculation
from ._common import get_response, handle_error, get_jwt


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
        try:
            match = Match.objects.get(id=oid)
            match.update(**request.get_json())
            match.reload()
            
            if not match.needs_confirmations() and not match.score_posted:
                err = calc_scores(match)
                if err is not None: raise ValueError
                print("match confirmed")

            claims = get_jwt()
            # if an admin starts a recalculation process
            # it's the only way to bypass the score_posted restriction
            if match.recalculate and claims["is_admin"]:
                start_recalculation(match)
                print("match and scores recalculated")
            
        except OperationError:
            return handle_error(f"error updating match in database: {oid}")
        except DoesNotExist:
            return handle_error(f"error updating match in database, match not found by oid: {oid}")
        except ValueError:
            return handle_error(f"{err} - error updating match with id: {oid}, calculations went wrong")
        except RuntimeError:
            return handle_error(f"error updating match - a clan cannot play against itself")
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
            # select grenzt angefragte Felder ein, z.B. select=match_id kommt nur
            # die match_id zurück, nciht das ganze Objekt aus der DB
            select = request.args.get('select')
            match_id = request.args.get('match_id')
            player_dist1 = request.args.get('player_dist1')
            player_dist2 = request.args.get('player_dist2')
            clans1_ids = request.args.get('clans1_ids')
            clans2_ids = request.args.get('clans2_ids')
            # coop1_id = request.args.get('coop1_id')
            # clan2_id = request.args.get('clan2_id')
            # coop2_id = request.args.get('coop2_id')
            conf1 = request.args.get('conf1')
            conf2 = request.args.get('conf2')
            date = request.args.get('date')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')

            fields = select.split(',') if select != None else []
                
            where = Q() # to perform advanced queries
            # see the doc: https://docs.mongoengine.org/guide/querying.html#advanced-queries
            # note, '&=' is the 'assign intersection operator'
            if match_id != None: where &= Q(match_id=match_id)
            #if clans1_ids != None: where &= (Q(clans1_ids=clans1_ids) | Q(clan2_id=clan_id))
            if clans1_ids != None: where &= Q(clans1_ids=clans1_ids)
            if clans2_ids != None: where &= Q(clans2_ids=clans2_ids)
            if player_dist1 != None: where &= Q(clans1=player_dist1)
            #if coop1_id != None: where &= Q(coop1_id=coop1_id)
            if player_dist2 != None: where &= Q(clans2=player_dist2)
            #if coop2_id != None: where &= Q(coop2_id=coop2_id)
            if conf1 != None: where &= Q(conf1=conf1)
            if conf2 != None: where &= Q(conf2=conf2)
            if date != None: where &= Q(date=date)
            # TODO: lesbares Datumsformat bei Anfrage mit Konvertierung
            if date_from != None: where &= Q(date__gte=date_from)
            if date_to != None: where &= Q(date__lte=date_to)

            matches = Match.objects(where).only(*fields)
                        
            return get_response(matches)
        
        except:
            return handle_error(f'error getting matches')


    # add new match
    @jwt_required()
    def post(self):
        try:
            match = Match(**request.get_json())
            match = match.save()
            need_conf = match.needs_confirmations() # just to remind the user
            # a match will always need at least the confirmation of the other team
            # therefore, there is no point of creating the scores within the POST method
        except:
            return handle_error(f'error creating match in database')
        else:
            return get_response({"match_id": match.match_id, "confirmed": not need_conf})
