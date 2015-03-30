"""
Common Gnome object request handlers.
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from types import MethodType, FunctionType, BuiltinFunctionType, NoneType
from logging import Logger

import numpy
np = numpy

from .helpers import FQNamesToDict, PyClassFromName

from gnome.utilities.orderedcollection import OrderedCollection
from gnome.spill_container import SpillContainerPair

from webgnome_api.common.session_management import set_session_object


def CreateObject(json_obj, all_objects, deserialize_obj=True):
    '''
        The Main entry point to be used by our views.

        We want to be able to handle nested object payloads, so we need
        to traverse to all leaf objects and update them first
    '''
    json_obj = _DeserializeObject(json_obj)

    for o in ProcessJsonObjectTree(_CreateObject, json_obj, all_objects):
        pass

    return o


def UpdateObject(obj, json_obj, all_objects, deserialize_obj=True):
    '''
        The Main entry point to be used by our views.

        We want to be able to handle nested object payloads, so we need
        to traverse to all leaf objects and update them first
    '''
    json_obj = _DeserializeObject(json_obj)

    [o for o in ProcessJsonObjectTree(_UpdateObject, json_obj, all_objects)]


def _DeserializeObject(json_obj):
    '''
        The py_gnome deserialize method can handle nested payloads
    '''
    py_class = PyClassFromName(json_obj['obj_type'])

    return py_class.deserialize(json_obj)


def ProcessJsonObjectTree(function, payload, all_objects,
                          parent=None, attr_name=None):
    if (isinstance(payload, dict)):
        for k, v in payload.items():
            for o in ProcessJsonObjectTree(function, v, all_objects,
                                           payload, k):
                yield o

        obj = function(payload, parent, attr_name, all_objects)
        yield obj
    elif (isinstance(payload, (list, tuple))):
        for i, v in enumerate(payload):
            for o in ProcessJsonObjectTree(function, v, all_objects,
                                           payload, i):
                yield o


def _CreateObject(payload, parent, attr_name, all_objects):
    '''
        Get the payload's associated object or create one.
        Then assign it to the parent (json)objects attribute
    '''
    if 'obj_type' not in payload:
        'not a nested object, just pass the dict unchanged'
        obj = payload
    elif ObjectExists(payload, all_objects):
        obj = all_objects[ObjectId(payload)]
    else:
        py_class = PyClassFromName(payload['obj_type'])
        obj = py_class.new_from_dict(payload)
        all_objects[obj.id] = obj

    # link the object to its associated parent attribute
    try:
        parent[attr_name] = obj
    except:
        if parent is not None:
            raise

    return obj


def _UpdateObject(payload, parent, attr_name, all_objects):
    '''
        Update the object with its associated payload.
        Then assign it to the parent (json)objects attribute
    '''
    if ObjectExists(payload, all_objects):
        obj = all_objects[ObjectId(payload)]

        obj.update_from_dict(payload)

        # link the object to its associated parent attribute
        try:
            parent[attr_name] = obj
        except:
            if parent is not None:
                raise
        return obj
    else:
        return _CreateObject(payload, parent, attr_name, all_objects)


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


def RegisterObject(obj, request):
    '''
        Recursively register an object plus all contained child objects.
        Registering means we put the object somewhere it can be looked up
        in the Web API.
        We would mainly like to register PyGnome objects.  Others
        we probably don't care about.
    '''
    if (hasattr(obj, 'id')
            and not obj.__class__.__name__ == 'type'):
        # print 'RegisterObject(): registering:', (obj.__class__.__name__,
        #                                           obj.id)
        set_session_object(obj, request)
    if isinstance(obj, (list, tuple, OrderedCollection,
                        SpillContainerPair)):
        for i in obj:
            RegisterObject(i, request)
        pass
    elif hasattr(obj, '__dict__'):
        for k in dir(obj):
            attr = getattr(obj, k)
            if not (k.find('_') == 0
                    or isinstance(attr, (MethodType, FunctionType,
                                         BuiltinFunctionType,
                                         int, float, str, unicode, NoneType,
                                         Logger)
                                  )):
                # print 'RegisterObject(): recursing attr:', (k, type(attr))
                RegisterObject(attr, request)


def obj_id_from_url(request):
    '''
        The pyramid URL parser returns a tuple of 0 or more
        matching items, at least when using the * wild card
    '''
    obj_id = request.matchdict.get('obj_id')
    return obj_id[0] if obj_id else None


def obj_id_from_req_payload(json_request):
    return json_request.get('id')
