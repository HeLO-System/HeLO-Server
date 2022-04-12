# rest/clans.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist, LookUpError
from werkzeug.exceptions import BadRequest
from mongoengine.queryset.visitor import Q

from models.clan import Clan
from ._common import get_response, handle_error, admin_required, empty


class ClanApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            clan = Clan.objects.get(id=oid)
            return get_response(clan)
        except ValidationError:
            return {"error": "not a valid object id"}, 404
        except DoesNotExist:
                return {"error": "object does not exist"}, 404
        except Exception as e:
            return handle_error(f"""error getting clan from database,
                                clan not found by oid: {oid}
                                terminated with error: {e}""")
        

    # update clan by object id
    @jwt_required()
    def put(self, oid):
        try:
            clan = Clan.objects.get(id=oid)
            # todo - validate TODO: was ist mit validate gemeint?
            try:
                clan.update(**request.get_json())
                return '', 204
            except BadRequest:
                return {"error": "Faulty Request"}, 400
            except Exception as e:
                return handle_error(f"""error updating clan in database: {clan.tag}
                                    terminated with error: {e}""")
        except ValidationError:
                return {"error": "not a valid object id"}, 404
        except DoesNotExist:
                return {"error": "object does not exist"}, 404
        except Exception as e:
            return handle_error(f"""error updating clan in database
                                terminated with error: {e}""")

    # update clan by object id
    # admin only
    @admin_required()
    def delete(self, oid):
        try:
            clan = Clan.objects.get(id=oid)        
            try:
                clan = clan.delete()
                return '', 204
            except Exception as e:
                return handle_error(f"""error deleting clan in database: {clan.tag}
                                    terminated with error: {e}""")
        except ValidationError:
                return {"error": "not a valid object id"}, 404
        except DoesNotExist:
                return {"error": "object does not exist"}, 404
        except Exception as e:
            return handle_error(f"""error deleting clan in database
                                terminated with error: {e}""")


class ClansApi(Resource):
    
    # get all or filtered by clan tag
    def get(self):
        try:
            # optional, clan tag
            tag = request.args.get("tag")
            # optional, full name
            name = request.args.get("name")
            # optional, number of matches
            num = request.args.get("num")
            # optional, HeLO score 'gte' and 'lte'
            score_from = request.args.get("score_from")
            score_to = request.args.get("score_to")

            # optional, narrows the return to selected fields
            # should be a comma separated list
            select = request.args.get("select")

            fields = select.split(",") if select is not None else []

            # filter through the documents by assigning the intersection (&=)
            # for every query parameter one by one
            filter = Q()
            
            if not empty(tag): filter &= Q(tag__icontains=tag)
            if not empty(name): filter &= Q(name__icontains=name)
            if not empty(num): filter &= Q(num_matches=num)
            if not empty(score_from): filter &= Q(score__gte=score_from)
            if not empty(score_to): filter &= Q(score__lte=score_to)

            clans = Clan.objects(filter).only(*fields)
            return get_response(clans)

        except LookUpError:
            return {"error": f"cannot resolve field 'select={select}'"}, 400

        except:
            return handle_error(f'error getting clans')


    # add new clan
    # admin only
    @admin_required()
    def post(self):
        try:
            clan = Clan(**request.get_json())
            # todo - validate
            try:
                clan = clan.save()
                #return get_response({ "id": clan.id }) # weird error happening here, TODO: fix this
                return f"id: {clan.id}", 200
            except NotUniqueError:
                return handle_error(f"clan already exists in database: {clan.tag}")
            except ValidationError as e:
                return handle_error(f"required field is empty: {e}")
            except:
                return handle_error(f"error creating clan in database: {clan.tag}")
        except:
            return handle_error(f'error creating clans in database')
