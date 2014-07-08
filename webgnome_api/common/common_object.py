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


def UpdateObject(obj, json_obj, all_objects, deserialize_obj=True):
    '''
        Here we update our python object with a JSON payload

        For now, I don't think we will be too fancy about this.
        We will grow more sophistication as we need it.
    '''
    FillSparseObjectChildren(json_obj, all_objects)

    py_class = PyClassFromName(json_obj['obj_type'])

    if deserialize_obj:
        obj_dict = py_class.deserialize(json_obj)
    else:
        obj_dict = json_obj

    return UpdateObjectAttributes(obj, obj_dict.iteritems(), all_objects)


def UpdateObjectAttributes(obj, items, all_objects):
    return any([UpdateObjectAttribute(obj, k, v, all_objects)
                for k, v in items])


# TODO: This function has grown quite a bit in scope and should
#       probably be refactored.  Let's start by separating the update
#       functionality of the different data types.
def UpdateObjectAttribute(obj, attr, value, all_objects):
    if attr in ('id', 'obj_type', 'json_'):
        return False
    elif ValueIsJsonObject(value):
        if ObjectExists(value, all_objects):
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
                            bool, NoneType, weakref.ref,
                            datetime, timedelta)):
        if not getattr(obj, attr) == value:
            setattr(obj, attr, value)
            return True
    elif isinstance(value, (dict)):
        for k, v in value.iteritems():
            UpdateObject(getattr(obj, attr)[k], v, all_objects, False)
        return True
    elif isinstance(value, (list, tuple, ndarray, void)):
        obj_attr = getattr(obj, attr)
        if type(obj_attr) == tuple:
            obj_attr = list(obj_attr)  # change it to a mutable
            setattr(obj, attr, obj_attr)

        if type(obj_attr) in (ndarray, void):
            value = np.array(value)

            if not np.all(obj_attr == value):
                setattr(obj, attr, value)
                return True
        elif type(obj_attr) in (list, tuple,
                                OrderedCollection, SpillContainerPair):
            ret_value = False
            for i, (v1, v2) in enumerate(izip_longest(obj_attr, value)):
                # So basically we are going to reconcile two lists
                # this isn't too hard, but we want to return whether
                # an update was performed.
                # We are assuming that valid list items are not None
                # and if we encounter a None value in either side, it
                # means that one list was shorter than the other
                if v1 == None:
                    # Empty left index...
                    if ValueIsJsonObject(v2):
                        if ObjectExists(v2, all_objects):
                            obj_attr.append(all_objects[v2['id']])
                            UpdateObject(all_objects[v2['id']], v2,
                                         all_objects, False)
                            ret_value = True
                        else:
                            # I dunno...we could create the object here.
                            # But for right now we will punt.
                            print ('Warning: Cannot perform updates.  '
                                   'Our child JSON object refers to a '
                                   'py_gnome object that does not exist.')
                    else:
                        # TODO: lots of possible edge cases here.
                        obj_attr.append(v2)
                        ret_value = True
                elif v2 == None:
                    # Empty right index...truncate our left list and
                    # exit our loop
                    v1 = v1[:i]
                    ret_value = True
                    break
                else:
                    # left & right are both present...lets see if they match
                    if ValueIsJsonObject(v2):
                        if ObjectId(v1) == ObjectId(v2):
                            #print 'left & right are the same object'
                            ret_value = UpdateObject(v1, v2, all_objects,
                                                     False)
                        elif ObjectExists(v2, all_objects):
                            #print ('left is different than right '
                            #       'and right exists')
                            obj_attr[i] = all_objects[v2['id']]
                            UpdateObject(obj_attr[i], v2, all_objects, False)
                            ret_value = True
                        else:
                            # I dunno...we could create the object here.
                            # But for right now we will punt.
                            print ('Warning: Cannot perform updates.  '
                                   'Our child JSON object refers to a '
                                   'py_gnome object that does not exist.')
                    else:
                        if obj_attr[i] != v2:
                            obj_attr[i] = v2
                            ret_value = True
            return ret_value
        else:
            if not all(obj_attr == value):
                setattr(obj, attr, value)
                return True

    return False


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


def init_session_objects(session, force=False):
    if (not 'objects' in session) or force:
        print ('init_session_objects(): '
               'object dict does not exist. initializing it.')
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


def FillSparseObjectChildren(obj_dict, all_objects):
    for v in obj_dict.values():
        if ValueIsJsonObject(v):
            FillSparseObject(v, all_objects)
        elif (isinstance(v, dict)):
            FillSparseObjectChildren(v, all_objects)
        elif (isinstance(v, (list, tuple))):
            for item in v:
                if ValueIsJsonObject(item):
                    FillSparseObject(item, all_objects)

            [FillSparseObjectChildren(i, all_objects) for i in v
             if isinstance(i, dict)]


def FillSparseObject(obj_dict, all_objects):
    if ObjectExists(obj_dict, all_objects):
        found = all_objects[obj_dict['id']].serialize()

        upd_items = [(k, v) for k, v in found.iteritems()
                     if k not in obj_dict]
        obj_dict.update(upd_items)
