# rest/auth.py
import datetime
from enum import Enum

from flask import request, Response, current_app
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from mongoengine import DoesNotExist
from mongoengine.queryset.visitor import Q

from models.clan import Clan
from models.user import User
from ._common import get_response, handle_error, get_jwt, admin_required, empty


class Role(Enum):
    User = 'USER'
    Admin = 'ADMIN'
    TeamManager = 'TEAM_MANAGER'

class DiscordLogin(Resource):
    discord = None

    def __init__(self, discord):
        self.discord = discord

    def get(self):
        return self.discord.create_session(scope=['guilds.members.read'])


class DiscordCallback(Resource):
    discord = None

    def __init__(self, discord):
        self.discord = discord

    def __resolve_guild(self, user):
        guilds = user.fetch_guilds()
        required_guild_id = int(current_app.config['DISCORD_AUTH_SETTINGS']['guildId'])
        for g in guilds:
            if g.id == required_guild_id:
                return g

        return None

    def __resolve_roles_clans(self, user_guild):
        info = self.discord.request(f'/users/@me/guilds/{user_guild.id}/member')
        helo_roles = [Role.User.value]
        helo_clans = []
        for r in info['roles']:
            if r == current_app.config['DISCORD_AUTH_SETTINGS']['adminRole']:
                helo_roles.append(Role.Admin.value)
            elif r == current_app.config['DISCORD_AUTH_SETTINGS']['teamManagerRole']:
                helo_roles.append(Role.TeamManager.value)
            else:
                try:
                    clan = Clan.objects.get(role_id=r)
                    helo_clans.append(clan.tag)
                except DoesNotExist:
                    continue
                except Exception:
                    return handle_error(f"error resolving clan membership", 500)

        return helo_roles, helo_clans

    def get(self):
        self.discord.callback()
        user = self.discord.fetch_user()
        guild = self.__resolve_guild(user)

        if guild is None:
            return 'not in guild', 401

        helo_roles, helo_clans = self.__resolve_roles_clans(guild)
        access_token = create_access_token(
            identity=user.id,
            expires_delta=datetime.timedelta(hours=8),
            additional_claims={
                'roles': helo_roles,
                'clans': helo_clans,
            }
        )

        return access_token


class SignupApi(Resource):

    def post(self):
        try:
            j = request.get_json()
            user = User(**j)
            user.hash_password()
            if user.role == "admin":
                # admins do not demand :P
                user.role = None
            user.save()
            return get_response({'id': user.userid})
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
            return get_response({'token': access_token})
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
                # prevents non-admins from changing their role
                # by checking the additional claim in JWT
                if "role" in request.get_json().keys():
                    claims = get_jwt()
                    # TODO: muss in die doku rein
                    if not claims["is_admin"]:
                        return {"error": "non-admins are not allowed to change their role"}, 401
                user.update(**request.get_json())
                return '', 204
            except:
                return handle_error(f"error updating user in database: {user.userid}")
        except:
            return handle_error(f"error updating user in database, user not found by oid: {userid}")

    # delete user by object id
    @admin_required()
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
            name = request.args.get("name")
            clan = request.args.get("clan_id")

            filter = Q()
            if not empty(name): filter &= Q(name__icontains=name)
            if not empty(clan): filter &= Q(clan=clan)

            total = User.objects(filter).exclude("pin").count()
            users = User.objects(filter).exclude("pin")

            res = {
                "total": total,
                "items": users.to_json_serializable()
            }

            return get_response(res)

        except:
            return handle_error(f"Error getting user data")
