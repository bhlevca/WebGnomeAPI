"""
Common Gnome object request handlers.
"""
from itertools import izip_longest

import numpy
np = numpy
from numpy import ndarray, void

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


def UpdateObject(obj, json_obj, all_objects):
    '''
        Here we update our python object with a JSON payload

        For now, I don't think we will be too fancy about this.
        We will grow more sophistication as we need it.
    '''
    py_class = PyClassFromName(json_obj['obj_type'])

    obj_dict = py_class.deserialize(json_obj)
    LinkObjectChildren(obj_dict, all_objects)

    return UpdateObjectAttributes(obj, obj_dict.iteritems())


def LinkObjectChildren(obj_dict, all_objects):
    for k, v in obj_dict.items():
        if ValueIsJsonObject(v):
            if 'id' in v and v['id'] in all_objects:
                #print ('JSON object exists in session: '
                #       '{0}({1})'.format(v['obj_type'], v['id']))
                obj_dict[k] = all_objects[v['id']]
            else:
                #print ('JSON object does not exist in session: '
                #       '{0}'.format(v['obj_type']))
                obj = CreateObject(v, all_objects, False)
                all_objects[obj.id] = obj
                obj_dict[k] = obj
        elif (isinstance(v, dict)):
            # we are dealing with an ordinary dict.
            # We will try to link the dictionary items.
            LinkObjectChildren(v, all_objects)


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


def UpdateObjectAttributes(obj, items):
    return all([UpdateObjectAttribute(obj, k, v) for k, v in items])


def UpdateObjectAttribute(obj, attr, value):
    if attr in ('id', 'obj_type', 'json_'):
        return False

    if (not ValueIsJsonObject(value)
        and not ObjectAttributesAreEqual(getattr(obj, attr), value)):
        setattr(obj, attr, value)
        return True
    else:
        return False


def ObjectAttributesAreEqual(attr1, attr2):
    '''
        Recursive equality which includes sequence objects
        (not really dicts yet though)
    '''
    if not type(attr1) == type(attr2):
        return False

    if isinstance(attr1, (list, tuple, ndarray, void)):
        for x, y in izip_longest(attr1, attr2):
            if not ObjectAttributesAreEqual(x, y):
                # we want to short-circuit our iteration
                return False
        return True
    else:
        return attr1 == attr2


def obj_id_from_url(request):
    # the pyramid URL parser returns a tuple of 0 or more
    # matching items, at least when using the * wild card
    obj_id = request.matchdict.get('obj_id')
    return obj_id[0] if obj_id else None


def obj_id_from_req_payload(json_request):
    return json_request.get('id')


def init_session_objects(session):
    if not 'objects' in session:
        session['objects'] = {}
        session.changed()


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
