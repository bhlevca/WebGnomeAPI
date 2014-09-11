"""
Common Gnome object request handlers.
"""
import weakref

from types import NoneType
from datetime import datetime, timedelta
from itertools import izip_longest

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

import numpy
np = numpy
from numpy import ndarray, void

from gnome.utilities.orderedcollection import OrderedCollection
from gnome.spill_container import SpillContainerPair

from .helpers import (FQNamesToDict,
                      PyClassFromName)


def CreateObject(json_obj, all_objects, deserialize_obj=True):
    '''
        Here we create a python object from our JSON payload
    '''
    py_class = PyClassFromName(json_obj['obj_type'])

    if deserialize_obj:
        obj_dict = py_class.deserialize(json_obj)
    else:
        obj_dict = json_obj

    LinkObjectChildren(obj_dict, all_objects)

    return py_class.new_from_dict(obj_dict)


def UpdateObject(obj, json_obj, all_objects, deserialize_obj=True):
    '''
        The Main entry point to be used by our views.

        We want to be able to handle nested object payloads, so we need
        to traverse to all leaf objects and update them first
    '''

    _DeserializeObject(json_obj)

    # traverse our json_obj
    print '\nComplete Payload:'
    pp.pprint(json_obj)
    for o in TraversePayloadForJsonObjects(json_obj):
        print '\nTraversed Payload:'
        pp.pprint(o)

    return _UpdateObject(obj, json_obj, deserialize_obj=True)


def _DeserializeObject(json_obj):
    '''
        The py_gnome deserialize method can handle nested payloads
    '''
    py_class = PyClassFromName(json_obj['obj_type'])

    return py_class.deserialize(json_obj)


def TraversePayloadForJsonObjects(function, payload,
                                  parent=None, attr_name=None):
    if (isinstance(payload, dict)):
        for k, v in payload.items():
            for o in TraversePayloadForJsonObjects(function, v, payload, k):
                yield o
        yield (payload, parent, attr_name)
        # Alright, we would like to now apply actions against our
        # json objects.
        #
        #  If we are performing an update:
        #    - if the object exists:
        #      - Update the existing object
        #      - link the existing object in-place
    elif (isinstance(payload, (list, tuple))):
        for i, v in enumerate(payload):
            for o in TraversePayloadForJsonObjects(function, v, payload, i):
                yield o


def _UpdateObject(obj, payload):
    return obj.update_from_dict(payload)


def LinkObjectChildren(obj_dict, all_objects):
    for k, v in obj_dict.items():
        if ValueIsJsonObject(v):
            if ObjectExists(v, all_objects):
                obj_dict[k] = all_objects[v['id']]
            else:
                obj = CreateObject(v, all_objects, False)
                all_objects[obj.id] = obj
                obj_dict[k] = obj
        elif (isinstance(v, dict)):
            LinkObjectChildren(v, all_objects)
        elif (isinstance(v, (list, tuple))):
            # we are dealing with a sequence.
            # We will try to link the list items.
            # TODO: this is kinda clunky, we should rethink and refactor
            for i, v2 in enumerate(v):
                if ValueIsJsonObject(v2):
                    if ObjectExists(v2, all_objects):
                        v[i] = all_objects[v2['id']]
                    else:
                        obj = CreateObject(v2, all_objects, False)
                        all_objects[obj.id] = obj
                        v[i] = obj

            [LinkObjectChildren(i, all_objects) for i in v
             if isinstance(i, dict)]


def ValueIsJsonObject(value):
    return (isinstance(value, dict)
            and 'obj_type' in value)


def ObjectId(obj):
    try:
        ident = obj['id']  # JSON Object
    except:
        try:
            ident = obj.id  # Gnome Object
        except:
            ident = id(obj)  # any other object

    return ident


def ObjectExists(value, all_objects):
    return ObjectId(value) in all_objects


def ObjectImplementsOneOf(model_object, obj_types):
    '''
        Here we determine if our python object type is contained within a set
        of implemented object types.

        :param model_obj: python object
        :param obj_types: list of fully qualified object names.

        TODO: check the object scope as well as the name
    '''
    if model_object.__class__.__name__ in FQNamesToDict(obj_types):
        return True

    return False


def obj_id_from_url(request):
    # the pyramid URL parser returns a tuple of 0 or more
    # matching items, at least when using the * wild card
    obj_id = request.matchdict.get('obj_id')
    return obj_id[0] if obj_id else None


def obj_id_from_req_payload(json_request):
    return json_request.get('id')
