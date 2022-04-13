# rest/matches.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import DoesNotExist, OperationError, LookUpError
from mongoengine.queryset.visitor import Q
from datetime import datetime

from models.match import Match
from logic.calculations import calc_scores
from logic.recalculations import start_recalculation
from ._common import get_response, handle_error, get_jwt, empty


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
            select = request.args.get("select")
            match_id = request.args.get("match_id")
            # comma separated list (or single entry)
            # e.g. clan_ids=123,456
            clan_ids = request.args.get("clan_ids")
            clan_ids = clan_ids.split(",") if clan_ids is not None else []
            caps = request.args.get("caps")
            caps_from = request.args.get("caps_from")
            map = request.args.get("map")
            duration_from = request.args.get("duration_from")
            duration_to = request.args.get("duration_to")
            factor = request.args.get("factor")
            conf = request.args.get("conf")
            event = request.args.get("event")

            date = request.args.get("date")
            date_from = request.args.get("date_from")
            date_to = request.args.get("date_to")

            # take the query string and split it by '-'
            # typecast the strings into integers and deliver them as year, month, day to
            # the datetime constructor
            if not empty(date):
                date = datetime(*[int(d) for d in date.split("-")])
            if not empty(date_from):
                date_from = datetime(*[int(d) for d in date_from.split("-")])
            if not empty(date_to):
                date_to = datetime(*[int(d) for d in date_to.split("-")])

            fields = select.split(',') if select is not None else []

            # filter through the documents by assigning the intersection (&=)
            # for every query parameter one by one  
            filter = Q()

            if not empty(match_id): filter &= Q(match_id__icontains=match_id)
            for id in clan_ids:
                if not empty(id): filter &= (Q(clans1_ids=id) | Q(clans2_ids=id))
            if not empty(caps): filter &= (Q(caps1=caps) | Q(caps2=caps))
            if not empty(caps_from): filter &= (Q(caps1__gte=caps_from) | Q(caps2__gte=caps_from))
            if not empty(map): filter &= Q(map__icontains=map)
            if not empty(duration_from): filter &= Q(duration__gte=duration_from)
            if not empty(duration_to): filter &= Q(duration__lte=duration_to)
            if not empty(factor): filter &= Q(factor=factor)
            if not empty(conf): filter &= (Q(conf1=conf) | Q(conf2=conf))
            if not empty(event): filter &= Q(event__icontains=event)

            if not empty(date): filter &= Q(date=date)
            # TODO: lesbares Datumsformat bei Anfrage mit Konvertierung
            # edit: done
            if not empty(date_from): filter &= Q(date__gte=date_from)
            if not empty(date_to): filter &= Q(date__lte=date_to)

            # significantly faster than len(), because it's server-sided
            total = Match.objects(filter).only(*fields).count()
            matches = Match.objects(filter).only(*fields)

            res = {
                "total": total,
                "items": matches.to_json_serializable()
            }
                        
            return get_response(res)
        
        except LookUpError:
            return {"error": f"cannot resolve field 'select={select}'"}, 400

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
