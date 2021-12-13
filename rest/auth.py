# rest/auth.py
import datetime
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from database.models import User
from ._common import *


class SignupApi(Resource):
    
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

            access_token = create_access_token(identity=user.userid, expires_delta=datetime.timedelta(days=7))
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
                