# rest/events.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from models.event import Event
from ._common import get_response, handle_error


class EventApi(Resource):
    
    # get by object id
    def get(self, oid):
        try:
            event = Event.objects.get(id=oid)
            return get_response(event)
        except:
            return handle_error(f"error getting event from database, event not found by oid: {oid}")
        

    # update event by object id
    @jwt_required()
    def put(self, oid):
        try:
            event = Event.objects.get(id=oid)        
            try:
                event.update(**request.get_json())
                return '', 204
            except:
                return handle_error(f"error updating event in database: {event.tag}")
        except:
            return handle_error(f"error updating event in database, event not found by oid: {oid}")

    # update event by object id
    @jwt_required()
    def delete(self, oid):
        try:
            event = Event.objects.get(id=oid)        
            try:
                event = event.delete()
                return '', 204
            except:
                return handle_error(f"error deleting event in database: {event.tag}")
        except:
            return handle_error(f"error deleting event in database, event not found by oid: {oid}")
        


class EventsApi(Resource):
    
    # get all or filtered by event tag
    def get(self):
        try:
            tag = request.args.get('tag')

            if tag == None:
                return get_response(Event.objects())
            else:
                events = Event.objects(tag=tag)
                if len(events) != 1:
                    return handle_error(f'no event found for: {tag}')
                else:
                    return get_response(events[0])
        except:
            return handle_error(f'error getting events')


    # add new event
    @jwt_required()
    def post(self):
        try:
            event = Event(**request.get_json())
            try:
                event = event.save()
                return get_response({ "id": event.id })
            except NotUniqueError:
                return handle_error(f"event already exists in database: {event.tag}")
            except:
                return handle_error(f"error creating event in database: {event.tag}")
        except:
            return handle_error(f'error creating event in database')

