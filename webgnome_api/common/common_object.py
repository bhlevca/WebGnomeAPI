"""
Common Gnome object request handlers.
"""
import weakref

from types import NoneType
from datetime import datetime

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

    print 'CreateObject(): json_obj:'
    pp.pprint(json_obj)
    if deserialize_obj:
        obj_dict = py_class.deserialize(json_obj)
    else:
        obj_dict = json_obj
    print 'CreateObject(): obj_dict:'
    pp.pprint(obj_dict)

    LinkObjectChildren(obj_dict, all_objects)
    print 'CreateObject(): linked obj_dict:'
    pp.pprint(obj_dict)

    return py_class.new_from_dict(obj_dict)


def LinkObjectChildren(obj_dict, all_objects):
    for k, v in obj_dict.items():
        if ValueIsJsonObject(v):
            if 'id' in v and v['id'] in all_objects:
                obj_dict[k] = all_objects[v['id']]
            else:
                obj = CreateObject(v, all_objects, False)
                all_objects[obj.id] = obj
                obj_dict[k] = obj
        elif (isinstance(v, dict)):
            # we are dealing with an ordinary dict.
            # We will try to link the dictionary items.
            LinkObjectChildren(v, all_objects)
        elif (isinstance(v, (list, tuple))):
            # we are dealing with a sequence.
            # We will try to link the list items.
            for i, v2 in enumerate(v):
                if ValueIsJsonObject(v2):
                    if 'id' in v2 and v2['id'] in all_objects:
                        v[i] = all_objects[v2['id']]
                    else:
                        obj = CreateObject(v2, all_objects, False)
                        all_objects[obj.id] = obj
                        v[i] = obj

            [LinkObjectChildren(i, all_objects) for i in v
             if isinstance(i, dict)]
        else:
            print ('LinkObjectChildren(): do not know how to link (k,v):',
                   (k, v, type(v))
                   )


def UpdateObject(obj, json_obj, all_objects, deserialize_obj=True):
    '''
        Here we update our python object with a JSON payload

        For now, I don't think we will be too fancy about this.
        We will grow more sophistication as we need it.
    '''
    py_class = PyClassFromName(json_obj['obj_type'])

    if deserialize_obj:
        obj_dict = py_class.deserialize(json_obj)
    else:
        obj_dict = json_obj

    return UpdateObjectAttributes(obj, obj_dict.iteritems(), all_objects)


def UpdateObjectAttributes(obj, items, all_objects):
    return all([UpdateObjectAttribute(obj, k, v, all_objects)
                for k, v in items])


def UpdateObjectAttribute(obj, attr, value, all_objects):
    if attr in ('id', 'obj_type', 'json_'):
        return False
    elif ValueIsJsonObject(value):
        if 'id' in value and value['id'] in all_objects:
            return UpdateObject(all_objects[value['id']], value, all_objects,
                                False)
        else:
            # TODO: should we raise an exception here?
            print ('Warning: Cannot perform updates.  '
                   'Our child JSON object refers to a py_gnome object '
                   'that does not exist.')
            return False
    elif isinstance(value, (int, float, long, complex,
                            str, unicode, bytearray, buffer,
                            set,
                            bool, NoneType, weakref.ref, datetime)):
        if not getattr(obj, attr) == value:
            setattr(obj, attr, value)
            return True
    elif isinstance(value, (dict)):
        for k, v in value.iteritems():
            UpdateObject(getattr(obj, attr)[k], v, all_objects, False)
        return True
    elif isinstance(value, (list, tuple, ndarray, void)):
        obj_attr = getattr(obj, attr)

        if type(obj_attr) in (ndarray, void):
            value = np.array(value)

            if not np.all(obj_attr == value):
                obj_attr[:] = value
                return True
        elif type(obj_attr) in (list, tuple,
                                OrderedCollection, SpillContainerPair):
            if not all([v1 == v2
                        for v1, v2 in zip(obj_attr, value)]):
                setattr(obj, attr, value)
                return True
        else:
            if not all(obj_attr == value):
                setattr(obj, attr, value)
                return True

    return False


def ValueIsJsonObject(value):
    return (isinstance(value, dict)
            and 'obj_type' in value)


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


def init_session_objects(session, force=False):
    if (not 'objects' in session) or force:
        session['objects'] = {}
        session.changed()


def get_session_objects(session):
    init_session_objects(session)
    return session['objects']


def get_session_object(obj_id, session):
    init_session_objects(session)

    if obj_id in session['objects']:
        return session['objects'][obj_id]
    else:
        return None


def set_session_object(obj, session):
    init_session_objects(session)

    try:
        session['objects'][obj.id] = obj
    except AttributeError:
        session['objects'][id(obj)] = obj

    session.changed()
