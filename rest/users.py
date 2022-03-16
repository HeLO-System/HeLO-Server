# rest/auth.py
import datetime
from flask import request
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from mongoengine.errors import NotUniqueError
from database.models import User
from ._common import *


class SignupApi(Resource):
    
    @admin_required()
    def post(self):
        try:
            j = request.get_json()
            user = User(**j)
            user.hash_password()
            user.save()
            return get_response({ 'id': user.userid })
        except:
            return handle_error("Error signing up")
    
    
class LoginApi(Resource):
    
    def post(self):
        try:
            body = request.get_json()
            user = User.objects.get(userid=body.get('userid'))
            authorized = user.check_password(body.get('pin'))
            if not authorized:
                return {'error': 'userid or pin invalid'}, 401

            if user.role == "admin":
                print("admin requested JWT token")
                access_token = create_access_token(identity=user.userid,
                                                    expires_delta=datetime.timedelta(days=7),
                                                    additional_claims={"is_admin": True})
            else:
                print("non-admin requested JWT token")
                access_token = create_access_token(identity=user.userid,
                                                    expires_delta=datetime.timedelta(days=7),
                                                    additional_claims={"is_admin": False})
            return get_response({ 'token': access_token })
        except:
            return handle_error("Error logging in")
    
    
class UserApi(Resource):
    
    # get user by discord userid
    def get(self, userid):
        try:        
            if userid == None:
                return Response(handle_error("no userid provided"), mimetype="application/json", status=500)
            else:
                user = User.objects(userid=userid)
                if len(user) != 1:
                    return handle_error(f'no user found for: {userid}')
                else:
                    return get_response(user[0])
        except:
            return handle_error(f"Error getting user data for {userid}")


    # update user by object id
    @jwt_required()
    def put(self, userid):
        try:
            user = User.objects.get(userid=userid)        
            try:
                user.update(**request.get_json())
                return '', 204
            except:
                return handle_error(f"error updating user in database: {user.userid}")
        except:
            return handle_error(f"error updating user in database, user not found by oid: {userid}")

    # update user by object id
    @jwt_required()
    def delete(self, userid):
        try:
            user = User.objects(userid=userid)
            try:
                user = user.delete()
                return '', 204
            except:
                return handle_error(f"error deleting user in database: {user.userid}")
        except:
            return handle_error(f"error deleting user in database, user not found by oid: {userid}")
        
        
class UsersApi(Resource):
    
    # get all or filtered by clan tag
    def get(self):
        try:        
            name = request.args.get('name')
            name_like = request.args.get('name_like')
            
            if name == None:
                if name_like == None:
                    return get_response(User.objects())
                else:
                    users = User.objects(name__icontains=name_like)
            else:
                users = User.objects(name=name)
            if len(users) == 0:
                return handle_error(f'no user found for: {name}')
            else:
                return get_response(users)
        except:
            return handle_error(f"Error getting user data")



    # add new user
    @jwt_required()
    def post(self):
        try:
            user = User(**request.get_json())
            try:
                user = user.save()
                return get_response({ "id": user.id })
            except NotUniqueError:
                return handle_error(f"user already exists in database: {user.userid}")
            except:
                return handle_error(f"error creating user in database: {user.userid}")
        except:
            return handle_error(f'error creating users in database')

