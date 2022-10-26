# rest/matches.py
import json
from datetime import datetime
from re import M
from urllib.parse import urlparse

import requests
from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from logic.calculations import calc_scores
from logic.recalculations import start_recalculation
from models.clan import Clan
from models.console.console_match import ConsoleMatch
from models.console.console_score import ConsoleScore
from models.match import Match, Type
from models.score import Score
from models.user import Role
from mongoengine.errors import (
    DoesNotExist,
    LookUpError,
    NotUniqueError,
    OperationError,
    ValidationError,
)
from mongoengine.queryset.visitor import Q
from schemas.query_schemas import MatchQuerySchema
from werkzeug.exceptions import BadRequest

from ._common import (
    admin_required,
    empty,
    get_jwt,
    get_response,
    handle_error,
    validate_schema,
)


def get_match_score_diff(match_id: str, clan_id: str, console: bool) -> float:
    score: Type[Score] | Type[ConsoleScore] = Score if not console else ConsoleScore

    match_score: Type[Score] | Type[ConsoleScore] = score.objects.get(
        match_id=match_id, clan=clan_id
    )
    try:
        last_score: int = score.objects.get(
            clan=clan_id, num_matches=match_score.num_matches - 1
        ).score
    except DoesNotExist:
        last_score = 1000 if console else 600
    return float(match_score.score - last_score)


def transform_match(match, console=False):
    for i in range(1, 3):
        players: int = match[f"players{i}"] if console else match["players"]

        match[f"clans{i}"] = [
            {
                "id": id,
                "score_diff": get_match_score_diff(match["match_id"], id, console)
                if match["score_posted"]
                else None,
                "players": match[f"player_dist{i}"][j]
                if match[f"player_dist{i}"][j:]
                else players,
            }
            for j, id in enumerate(match[f"clans{i}_ids"])
        ]

        del match[f"clans{i}_ids"]
        del match[f"player_dist{i}"]
    return match


###############################################
#                   PC APIs                   #
###############################################


class MatchApi(Resource):
    def get(self, match_id):
        try:
            match: Match = Match.objects.get(match_id=match_id).to_dict()

            return get_response(transform_match(match))
        except DoesNotExist:
            return handle_error("object does not exist", 404)
        except Exception as e:
            return handle_error(
                f"error getting match from database, terminated with error: {e}", 500
            )

    @admin_required()
    def put(self, match_id):
        """
        TODO: This method could, in it's current form, be used to bypass match confirmation (by passing in the conf1 and conf2
        fields in the patch request. Hence, to prevent this, this method is for admins only, for now.
        """
        try:
            # validation, if request contains all required fields and types
            match = Match(**request.get_json())
            match.validate()
            # must be a QuerySet, therefore no get()
            match_qs = Match.objects(match_id=match_id)
            res = match_qs.update_one(
                upsert=True, **request.get_json(), full_result=True
            )
            # load Match object for the logic instead of working with the QuerySet
            match = Match.objects.get(match_id=match_id)
            if not match.needs_confirmations() and not match.score_posted:
                err = calc_scores(match)
                if err is not None:
                    raise ValueError

            if res.raw_result.get("updatedExisting"):
                return get_response(
                    {"message": f"replaced match with id: {match_id}"}, 200
                )
        except ValidationError as e:
            return handle_error(f"validation failed: {e}", 400)
        except ValueError as err:
            return handle_error(
                f"{err} - error updating match with id: {match_id}, calculations went wrong",
                400,
            )
        except RuntimeError:
            return handle_error(
                f"error updating match - a clan cannot play against itself", 400
            )
        else:
            return get_response({"message": f"created match with id: {match_id}"}, 201)

    @admin_required()
    def patch(self, match_id):
        """
        TODO: This method could, in it's current form, be used to bypass match confirmation (by passing in the conf1 and conf2
        fields in the patch request. Hence, to prevent this, this method is for admins only, for now.
        """
        try:
            match = Match.objects.get(match_id=match_id)
            match.update(**request.get_json())
            match.reload()

            if not match.needs_confirmations() and not match.score_posted:
                err = calc_scores(match)
                if err is not None:
                    raise ValueError
                print("match confirmed")

            claims = get_jwt()
            # if an admin starts a recalculation process
            # it's the only way to bypass the score_posted restriction
            if match.recalculate:
                if not claims["is_admin"]:
                    raise OperationError
                else:
                    start_recalculation(match)
                    print("match and scores recalculated")

        except DoesNotExist:
            return handle_error(
                f"error updating match in database, match not found by oid: {match_id}",
                404,
            )
        except ValueError as err:
            return handle_error(
                f"{err} - error updating match with id: {match_id}, calculations went wrong",
                400,
            )
        except RuntimeError:
            return handle_error(
                f"error updating match - a clan cannot play against itself", 400
            )
        else:
            return get_response("", 204)

    @jwt_required()
    def delete(self, match_id):
        """
        Delete a match by its ID. A match can only be deleted, if:
        - the match is not yet posted
        - the match was confirmed by the requester
        - the requester is a team manager of one of the participating clans
        or
        - the requester is an admin (bypassing all the conditions above)
        """
        try:
            claims = get_jwt()
            is_admin = Role.Admin.value in claims["roles"]
            is_teammanager = Role.TeamManager.value in claims["roles"]
            match = Match.objects.get(match_id=match_id)

            if not is_admin and not is_teammanager:
                return handle_error("object does not exist", 404)

            if (
                not match.can_be_deleted(get_jwt_identity(), claims["clans"])
                and not is_admin
            ):
                return handle_error("object does not exist", 404)

            match.delete()

        except ValidationError:
            return handle_error("not a valid object id", 400)
        except DoesNotExist:
            return handle_error("object does not exist", 404)
        except Exception as e:
            return handle_error(
                f"error deleting match in database, terminated with error: {e}", 500
            )
        else:
            return get_response("", 204)


class MatchesApi(Resource):
    def get(self):
        try:
            validate_schema(MatchQuerySchema(), request.args)
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
            side = request.args.get("side")

            # optional, quality of life query parameters
            limit = request.args.get("limit", default=0, type=int)
            offset = request.args.get("offset", default=0, type=int)
            sort_by = request.args.get("sort_by", default=None, type=str)
            # descending order
            desc = request.args.get("desc", default=None, type=str)

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

            fields = select.split(",") if select is not None else []

            # filter through the documents by assigning the intersection (&=)
            # for every query parameter one by one
            filter = Q()

            if not empty(match_id):
                filter &= Q(match_id__icontains=match_id)
            for id in clan_ids:
                if not empty(id):
                    filter &= Q(clans1_ids=id) | Q(clans2_ids=id)
            if not empty(caps):
                filter &= Q(caps1=caps) | Q(caps2=caps)
            if not empty(caps_from):
                filter &= Q(caps1__gte=caps_from) | Q(caps2__gte=caps_from)
            if not empty(map):
                filter &= Q(map__icontains=map)
            if not empty(duration_from):
                filter &= Q(duration__gte=duration_from)
            if not empty(duration_to):
                filter &= Q(duration__lte=duration_to)
            if not empty(factor):
                filter &= Q(factor=factor)
            if not empty(conf):
                filter &= Q(conf1=conf) | Q(conf2=conf)
            if not empty(event):
                filter &= Q(event__icontains=event)
            if not empty(side):
                if len(clan_ids) > 0:
                    # if a side has been specified, the clan id must be on that side
                    cond1 = Q(clans1_ids=str(clan_ids[0])) & Q(side1__iexact=side)
                    cond2 = Q(clans2_ids=str(clan_ids[0])) & Q(side2__iexact=side)
                    filter &= cond1 | cond2
                else:
                    raise BadRequest("missing clan id")

            if not empty(date):
                filter &= Q(date=date)
            # TODO: lesbares Datumsformat bei Anfrage mit Konvertierung
            # edit: done
            if not empty(date_from):
                filter &= Q(date__gte=date_from)
            if not empty(date_to):
                filter &= Q(date__lte=date_to)

            filtered = Match.objects(filter)
            limited = filtered.only(*fields).limit(limit).skip(offset)
            if not empty(desc) and desc:
                matches = limited.order_by(f"-{sort_by}")
            else:
                matches = limited.order_by(f"+{sort_by}")

        except BadRequest as e:
            # TODO: better error response
            return handle_error(f"Bad Request, terminated with: {e}", 400)
        except LookUpError:
            return handle_error(f"cannot resolve field 'select={select}'", 400)
        except Exception as e:
            return handle_error(
                f"error getting matches, terminated with error: {e}", 500
            )
        else:
            return get_response(
                {
                    "matches": [
                        transform_match(match)
                        for match in json.loads(matches.to_json())
                    ],
                    "meta": {
                        "count": matches.count(True),
                        "offset": offset,
                        "total_count": filtered.count(False),
                    },
                }
            )

    # add new match
    @admin_required()
    def post(self):
        try:
            match = Match(**request.get_json())
            match.conf1 = get_jwt_identity()
            match.conf2 = ""
            match.score_posted = False
            match = match.save()

            claims = get_jwt()
            if Role.Admin.value in claims["roles"]:
                match.conf2 = get_jwt_identity()
                err = calc_scores(match)
                if err is not None:
                    raise ValueError

        except NotUniqueError:
            return handle_error(f"match already exists in database", 400)
        except ValidationError as e:
            return handle_error(f"required field is empty: {e}")
        except Exception as e:
            return handle_error(
                f"error creating match in database, terminated with error: {e}", 500
            )
        else:
            return get_response(
                {
                    "match_id": match.match_id,
                    "confirmed": not match.needs_confirmations(),
                },
                201,
            )


class MatchesNotificationApi(Resource):
    """
    Temporary API to report matches to the discord report-match channel. This API will be removed, once reporting a match
    is done using the MatchesApi match report workflow.
    """

    def __clan_player_count(
        self, distribution: "list[int]", clans: "list[Clan]", player_count: int or None
    ) -> str:
        if distribution:
            res = " & ".join(
                [
                    "**" + clan.tag + "** (" + str(distribution[i]) + ")"
                    for i, clan in enumerate(clans)
                ]
            )
            if len(distribution) > 1:
                res += " => " + str(sum(distribution))
        else:
            res = (
                " & ".join(["**" + clan.tag + "**" for clan in clans])
                + "("
                + player_count
                + ")"
            )

        return res

    def __build_webhook_payload(self, match: Match, posting_user: dict) -> dict:
        event_comment = ""
        if match.type == Type.Competetive:
            event_comment = " (%s)" % match.event

        axis = self.__clan_player_count(
            match.player_dist1, Clan.objects(id__in=match.clans1_ids), match.players
        )
        allies = self.__clan_player_count(
            match.player_dist2, Clan.objects(id__in=match.clans2_ids), match.players
        )

        caps = "/".join(match.strongpoints)
        fields = [
            f"**{match.type.value}{event_comment}**",
            match.date,
            f"Axis: {axis}",
            f"Allies: {allies}",
            f"Result: **{match.caps1}:{match.caps2}** in **{match.duration}min**",
            f"Map: **{match.map}**",
            f"Caps: {caps}",
        ]
        if match.stream_url:
            fields.append(
                f"Stream: [{urlparse(match.stream_url).hostname}]({match.stream_url})"
            )

        return {
            "embeds": [
                {
                    "color": 16750848,
                    "author": {
                        "name": posting_user["friendly_name"],
                        "icon_url": posting_user["avatar"],
                    },
                    "title": match.match_id,
                    "url": "https://helo-system.de/matches/" + match.match_id,
                    "description": "\n".join(fields),
                }
            ],
        }

    @admin_required()
    def post(self):
        try:
            match = Match(**request.get_json())
            if (
                match.players > 100
                or sum(match.player_dist1) > 50
                or sum(match.player_dist2) > 50
            ):
                return handle_error("too many players", 400)
            claims = get_jwt()
            if Role.Admin.value not in claims["roles"]:
                if Role.TeamManager.value not in claims["roles"]:
                    return handle_error("you're not a team-manager", 403)

                team_manager_of_one_clan = False
                for c in claims["clans"]:
                    if c in (match.clans1_ids + match.clans2_ids):
                        team_manager_of_one_clan = True
                        break
                if not team_manager_of_one_clan:
                    return handle_error(
                        "you're not a teammanager of one of the clans of this match",
                        403,
                    )

            res = requests.post(
                current_app.config["DISCORD_REPORT_MATCH_WEBHOOK"],
                json=self.__build_webhook_payload(match, claims),
            )
            if res.status_code != 204:
                return handle_error(f"error while posting result: {res.text}", 500)
        except NotUniqueError:
            return handle_error("match already exists in database", 400)
        except ValidationError as e:
            return handle_error(f"required field is empty: {e}")
        except Exception as e:
            return handle_error(
                f"error creating match in database, terminated with error: {e}", 500
            )
        else:
            return get_response("", 201)


###############################################
#                CONSOLE APIs                 #
###############################################


class ConsoleMatchApi(Resource):

    # get by object id
    def get(self, match_id):
        try:
            match: ConsoleMatch = ConsoleMatch.objects.get(match_id=match_id).to_dict()

            return get_response(transform_match(match, True))

        except AttributeError:
            return handle_error(
                f"multiple errors: You did not provide a valid object id, instead I looked for a match with the match_id '{match_id}', but couldn't find any.",
                400,
            )
        except DoesNotExist:
            return handle_error("object does not exist", 404)
        except Exception as e:
            return handle_error(
                f"error getting match from database, terminated with error: {e}", 500
            )

    # update match by object id
    @admin_required()
    def put(self, match_id):
        try:
            # validation, if request contains all required fields and types
            match = ConsoleMatch(**request.get_json())
            match.validate()
            # must be a QuerySet, therefore no get()
            match_qs = ConsoleMatch.objects(match_id=match_id)
            res = match_qs.update_one(
                upsert=True, **request.get_json(), full_result=True
            )
            # load Match object for the logic instead of working with the QuerySet
            match = ConsoleMatch.objects.get(match_id=match_id)
            if not match.needs_confirmations() and not match.score_posted:
                err = calc_scores(match, console=True)
                if err is not None:
                    raise ValueError
                print("match confirmed")

            if res.raw_result.get("updatedExisting"):
                return get_response(
                    {"message": f"replaced match with id: {match_id}"}, 200
                )
        except ValidationError as e:
            return handle_error(f"validation failed: {e}", 400)
        except ValueError as err:
            return handle_error(
                f"{err} - error updating match with id: {match_id}, calculations went wrong",
                400,
            )
        except RuntimeError:
            return handle_error(
                f"error updating match - a clan cannot play against itself", 400
            )
        else:
            return get_response({"message": f"created match with id: {match_id}"}, 201)

    @admin_required()
    def patch(self, match_id):
        """
        TODO: This method could, in it's current form, be used to bypass match confirmation (by passing in the conf1 and conf2
        fields in the patch request. Hence, to prevent this, this method is for admins only, for now.
        """
        try:
            match = ConsoleMatch.objects.get(match_id=match_id)
            match.update(**request.get_json())
            match.reload()

            if not match.needs_confirmations() and not match.score_posted:
                err = calc_scores(match, console=True)
                if err is not None:
                    raise ValueError
                print("match confirmed")

            claims = get_jwt()
            # if an admin starts a recalculation process
            # it's the only way to bypass the score_posted restriction
            if match.recalculate:
                if not claims["is_admin"]:
                    raise OperationError
                else:
                    start_recalculation(match, console=True)
                    print("match and scores recalculated")

        except DoesNotExist:
            return handle_error(
                f"error updating match in database, match not found by oid: {match_id}",
                404,
            )
        except ValueError as err:
            return handle_error(
                f"{err} - error updating match with id: {match_id}, calculations went wrong",
                400,
            )
        except RuntimeError:
            return handle_error(
                f"error updating match - a clan cannot play against itself", 400
            )
        else:
            return get_response("", 204)

    # update match by object id
    @admin_required()
    def delete(self, match_id):
        try:
            match = ConsoleMatch.objects.get(match_id=match_id)
            match.delete()

        except ValidationError:
            return handle_error("not a valid object id", 400)
        except DoesNotExist:
            return handle_error("object does not exist", 404)
        except Exception as e:
            return handle_error(
                f"error deleting match in database, terminated with error: {e}", 500
            )
        else:
            return get_response("", 204)


class ConsoleMatchesApi(Resource):

    # get all or filtered by match id
    def get(self):
        try:
            validate_schema(MatchQuerySchema(), request.args)
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

            # optional, quality of life query parameters
            limit = request.args.get("limit", default=0, type=int)
            offset = request.args.get("offset", default=0, type=int)
            sort_by = request.args.get("sort_by", default=None, type=str)
            # descending order
            desc = request.args.get("desc", default=None, type=str)

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

            fields = select.split(",") if select is not None else []

            # filter through the documents by assigning the intersection (&=)
            # for every query parameter one by one
            filter = Q()

            if not empty(match_id):
                filter &= Q(match_id__icontains=match_id)
            for id in clan_ids:
                if not empty(id):
                    filter &= Q(clans1_ids=id) | Q(clans2_ids=id)
            if not empty(caps):
                filter &= Q(caps1=caps) | Q(caps2=caps)
            if not empty(caps_from):
                filter &= Q(caps1__gte=caps_from) | Q(caps2__gte=caps_from)
            if not empty(map):
                filter &= Q(map__icontains=map)
            if not empty(duration_from):
                filter &= Q(duration__gte=duration_from)
            if not empty(duration_to):
                filter &= Q(duration__lte=duration_to)
            if not empty(factor):
                filter &= Q(factor=factor)
            if not empty(conf):
                filter &= Q(conf1=conf) | Q(conf2=conf)
            if not empty(event):
                filter &= Q(event__icontains=event)

            if not empty(date):
                filter &= Q(date=date)
            # TODO: lesbares Datumsformat bei Anfrage mit Konvertierung
            # edit: done
            if not empty(date_from):
                filter &= Q(date__gte=date_from)
            if not empty(date_to):
                filter &= Q(date__lte=date_to)

            filtered = ConsoleMatch.objects(filter)
            limited = filtered.only(*fields).limit(limit).skip(offset)
            if not empty(desc) and desc:
                matches = limited.order_by(f"-{sort_by}")
            else:
                matches = limited.order_by(f"+{sort_by}")

        except BadRequest as e:
            # TODO: better error response
            return handle_error(f"Bad Request, terminated with: {e}", 400)
        except LookUpError:
            return handle_error(f"cannot resolve field 'select={select}'", 400)
        except Exception as e:
            return handle_error(
                f"error getting matches, terminated with error: {e}", 500
            )
        else:
            return get_response(
                {
                    "matches": [
                        transform_match(match, True)
                        for match in json.loads(matches.to_json())
                    ],
                    "meta": {
                        "count": matches.count(True),
                        "offset": offset,
                        "total_count": filtered.count(False),
                    },
                }
            )

    # add new match
    @admin_required()
    def post(self):
        try:
            match = ConsoleMatch(**request.get_json())
            match.conf1 = get_jwt_identity()
            match.conf2 = ""
            match.score_posted = False
            match = match.save()

            claims = get_jwt()
            if Role.Admin.value in claims["roles"]:
                match.conf2 = get_jwt_identity()
                err = calc_scores(match, console=True)
                if err is not None:
                    raise ValueError

        except NotUniqueError:
            return handle_error(f"match already exists in database", 400)
        except ValidationError as e:
            return handle_error(f"required field is empty: {e}")
        except Exception as e:
            return handle_error(
                f"error creating match in database, terminated with error: {e}", 500
            )
        else:
            return get_response(
                {
                    "match_id": match.match_id,
                    "confirmed": not match.needs_confirmations(),
                },
                201,
            )
