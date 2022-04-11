# rest/clans.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from werkzeug.exceptions import BadRequest
from database.models import Clan
from ._common import *


class ClanApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            clan = Clan.objects.get(id=oid)
            return get_response(clan)
        except ValidationError:
            return "not a valid object id", 404
        except DoesNotExist:
                return "object does not exist", 404
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
                return "Faulty Request", 400
            except Exception as e:
                return handle_error(f"""error updating clan in database: {clan.tag}
                                    terminated with error: {e}""")
        except ValidationError:
                return "not a valid object id", 404
        except DoesNotExist:
                return "object does not exist", 404
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
                return "not a valid object id", 404
        except DoesNotExist:
                return "object does not exist", 404
        except Exception as e:
            return handle_error(f"""error deleting clan in database
                                terminated with error: {e}""")


class ClansApi(Resource):
    
    # get all or filtered by clan tag
    def get(self):
        try:
            tag = request.args.get('tag')

            if tag is None:
                return get_response(Clan.objects())
            else:
                clans = Clan.objects(tag=tag)
                if len(clans) != 1:
                    return handle_error(f'no clan found for: {tag}')
                else:
                    return get_response(clans[0])
        except:
            return handle_error(f'error getting clans')


    # add new clan
    #@jwt_required()
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
