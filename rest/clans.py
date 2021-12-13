# rest/clans.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from database.models import Clan
from ._common import *


class ClanApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            clan = Clan.objects.get(id=oid)
            return get_response(clan)
        except:
            return handle_error(f"error getting clan from database, clan not found by oid: {oid}")
        

    # update clan by object id
    @jwt_required()
    def put(self, oid):
        try:
            clan = Clan.objects.get(id=oid)        
            try:
                clan.update(**request.get_json())
                return '', 204
            except:
                return handle_error(f"error updating clan in database: {clan.tag}")
        except:
            return handle_error(f"error updating clan in database, clan not found by oid: {oid}")

    # update clan by object id
    @jwt_required()
    def delete(self, oid):
        try:
            clan = Clan.objects.get(id=oid)        
            try:
                clan = clan.delete()
                return '', 204
            except:
                return handle_error(f"error deleting clan in database: {clan.tag}")
        except:
            return handle_error(f"error deleting clan in database, clan not found by oid: {oid}")
        


class ClansApi(Resource):
    
    # get all or filtered by clan tag
    def get(self):
        try:
            tag = request.args.get('tag')

            if tag == None:
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
    @jwt_required()
    def post(self):
        try:
            clan = Clan(**request.get_json())
            try:
                clan = clan.save()
                return get_response({ "id": clan.id })
            except NotUniqueError:
                return handle_error(f"clan already exists in database: {clan.tag}")
            except:
                return handle_error(f"error creating clan in database: {clan.tag}")
        except:
            return handle_error(f'error creating clans in database')

