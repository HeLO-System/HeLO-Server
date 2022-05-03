# rest/clans.py
from flask import request, redirect
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError, OperationError, ValidationError, DoesNotExist, LookUpError
from werkzeug.exceptions import BadRequest
from mongoengine.queryset.visitor import Q
from datetime import datetime

from models.clan import Clan
from models.score import Score
from schemas.query_schemas import ClanQuerySchema, ScoreHistoryQuerySchema
from ._common import get_response, handle_error, admin_required, empty, validate_schema

# https://stackoverflow.com/questions/30779584/flask-restful-passing-parameters-to-get-request
# https://www.programcreek.com/python/example/108223/marshmallow.validate.OneOf
# https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html?highlight=oneOf#marshmallow.validate.OneOf
# https://stackoverflow.com/questions/30779584/flask-restful-passing-parameters-to-get-request
# class QuerySchema(Schema):
#     select = fields.Str(required=True, validate=OneOf(["name"]))


class ClanApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            try:
                clan = Clan.objects.get(id=oid)
                # causes problems in frontend, removed for the time being
                # name = "-".join(clan.name.split())
                # return redirect('/clan/' + name)
            except ValidationError:
                clan = Clan.objects.search_text(oid).first()
                return get_response(clan)

        except AttributeError:
            return handle_error(f"multiple errors: You did not provide a valid object id, instead I looked for a clan with the name '{oid}', but couldn't find any.", 400)
        except DoesNotExist:
                return handle_error("object does not exist", 404)
        except Exception as e:
            return handle_error(f"error getting clan from database, clan not found by oid: {oid}, terminated with error: {e}", 500)


    # update clan by object id
    @jwt_required()
    def put(self, oid):
        try:
            # validation, if request contains all required fields and types
            clan = Clan(**request.get_json())
            clan.validate()
            # QuerySet
            clan_qs = Clan.objects(id=oid)
            # can also be upsert_one or update, more important is that we do this on a QuerySet
            # and not on a Document
            res = clan_qs.update_one(upsert=True, last_updated=datetime.now(), **request.get_json(), full_result=True)
            if res.raw_result.get("updatedExisting"):
                return get_response({"message": f"replaced clan with id: {oid}"}, 200)

        except BadRequest:
            return handle_error("Bad Request", 400)
        except ValidationError as e:
                return handle_error(f"validation failed: {e}", 400)
        except Exception as e:
            return handle_error(f"error updating clan in database, terminated with error: {e}", 500)
        else:
            return get_response({"message": f"created clan with id: {oid}"}, 201)


    @jwt_required()
    def patch(self, oid):
        try:
            clan = Clan.objects.get(id=oid)
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
            validate_schema(ClanQuerySchema(), request.args)
            # optional, clan tag
            tag = request.args.get("tag")
            # optional, full name
            name = request.args.get("name")
            # optional, number of matches
            num = request.args.get("num_matches")
            # optional, HeLO score 'gte' and 'lte'
            score_from = request.args.get("score_from")
            score_to = request.args.get("score_to")

            # optional, quality of life query parameters
            limit = request.args.get("limit", default=0, type=int)
            offset = request.args.get("offset", default=0, type=int)
            sort_by = request.args.get("sort_by", default=None, type=str)
            # descending order
            desc = request.args.get("desc", default=None, type=str)

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
            
            if not empty(desc) and desc:
                clans = Clan.objects(filter).only(*fields).limit(limit).skip(offset).order_by(f"-{sort_by}")
                return get_response(clans)
            
            clans = Clan.objects(filter).only(*fields).limit(limit).skip(offset).order_by(f"+{sort_by}")

        except BadRequest as e:
            # TODO: better error response
            return handle_error(f"Bad Request, terminated with: {e}", 400)
        except LookUpError:
            return handle_error(f"cannot resolve field 'select={select}'", 400)
        except Exception as e:
            return handle_error(f"error getting clans, terminated with error: {e}", 500)
        else:
            return get_response(clans)


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


class ScoreHistoryApi(Resource):

    def get(self, oid):
        try:
            validate_schema(ScoreHistoryQuerySchema(), request.args)
            # date in format: YYYY-MM-DD, history from 'start' to 'end'
            # alternative time range, from - to
            start = request.args.get("start")
            end = request.args.get("end")
            select = request.args.get("select")
            desc = request.args.get("desc")

            fields = select.split(",") if select is not None else []
            filter = Q(clan=oid)

            if not empty(start):
                start = datetime(*[int(d) for d in start.split("-")])
                filter &= Q(_created_at__gte=start)
            if not empty(end):
                # specify hour and minute, because otherwise:
                # 2022-04-01 at 17:32:03 > 2022-04-01 at 00:00:00 (which is the default value)
                end = datetime(*[int(d) for d in end.split("-")], hour=23, minute=59)
                filter &= Q(_created_at__lte=end)

            if not empty(desc) and desc:
                # descending oder
                scores = Score.objects(filter).only(*fields).order_by("-_created_at")
                return get_response(scores)
            scores = Score.objects(filter).only(*fields).order_by("+_created_at")

        except BadRequest as e:
            # TODO: better error response
            return handle_error(f"Bad Request, terminated with: {e}", 400)
        except LookUpError:
            return handle_error(f"cannot resolve field 'select={select}'", 400)
        except Exception as e:
            return handle_error(f"error getting clans, terminated with error: {e}", 500)
        else:
            return get_response(scores)
