# rest/clans.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError, OperationError, ValidationError, DoesNotExist, LookUpError
from requests import get
from werkzeug.exceptions import BadRequest
from mongoengine.queryset.visitor import Q
from datetime import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId

from models.clan import Clan
from ._common import get_response, handle_error, admin_required, empty


class ClanApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            # byte_oid = bytes(oid, encoding="utf-8")
            # print(byte_oid)
            # print(ObjectId.is_valid(ObjectId(oid)))
            try:
                clan = Clan.objects.get(id=oid)
            except ValidationError:
                #clan = Clan.objects(name__wholeword=oid).first()
                clan = Clan.objects.search_text(oid).first()
                res = {
                    "warning": "no valid object id",
                    "instead": f"first clan matching '{oid}'",
                    "result": clan.to_dict()
                }
                return get_response(res)

        except AttributeError:
            return handle_error(f"multiple errors: You did not provide a valid object id, instead I looked for a clan with the name '{oid}', but couldn't find any.", 400)
        except DoesNotExist:
                return handle_error("object does not exist", 404)
        except Exception as e:
            return handle_error(f"error getting clan from database, clan not found by oid: {oid}, terminated with error: {e}", 500)
        else:
            return get_response(clan, 200)


    # update clan by object id
    @jwt_required()
    def put(self, oid):
        try:
            clan = Clan.objects.get(id=oid)
            # todo - validate TODO: was ist mit validate gemeint?
            clan.update(last_updated=datetime.now(), **request.get_json())

        except BadRequest:
            return handle_error("Bad Request", 400)
        except ValidationError:
                return handle_error("not a valid object id", 400)
        except DoesNotExist:
                return handle_error("object does not exist", 404)
        except Exception as e:
            return handle_error(f"error updating clan in database, terminated with error: {e}", 500)
        else:
            return get_response("", 204)


    # update clan by object id
    # admin only
    @admin_required()
    def delete(self, oid):
        try:
            clan = Clan.objects.get(id=oid)        
            clan = clan.delete()

        except OperationError:
            return handle_error(f"Authorization failed", 401)
        except ValidationError:
                return handle_error("not a valid object id", 400)
        except DoesNotExist:
                return handle_error("object does not exist", 404)
        except Exception as e:
            return handle_error(f"error deleting clan in database, terminated with error: {e}", 500)
        else:
            return get_response("", 204)


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
            
            # significantly faster than len(), because it's server-sided
            total = Clan.objects(filter).only(*fields).count()
            clans = Clan.objects(filter).only(*fields)

            res = {
                "total": total,
                "items": clans.to_json_serializable()
            }

        except LookUpError:
            return handle_error(f"cannot resolve field 'select={select}'", 400)
        except Exception as e:
            return handle_error(f"error getting clans, terminated with error: {e}", 500)
        else:
            return get_response(res)


    # add new clan
    # admin only
    @admin_required()
    def post(self):
        try:
            clan = Clan(**request.get_json())
            # todo - validate
            clan = clan.save()

        except NotUniqueError:
            return handle_error(f"clan already exists in database: {clan.tag}", 400)
        except ValidationError as e:
            return handle_error(f"required field is empty: {e}")
        except Exception as e:
            return handle_error(f"error creating clans in database, terminated with error: {e}", 500)
        else:
            return get_response({"id": str(clan.id)}, 201)