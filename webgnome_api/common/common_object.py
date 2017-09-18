"""
    Common Gnome object request handlers.
"""
import os
import shutil
import urllib2
import ujson

import logging

from .helpers import FQNamesToDict, PyClassFromName

from gnome.utilities.orderedcollection import OrderedCollection
from gnome.spill_container import SpillContainerPair

from webgnome_api.common.session_management import set_session_object

log = logging.getLogger(__name__)


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
    except Exception:
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
        except Exception:
            if parent is not None:
                raise
        return obj
    else:
        return _CreateObject(payload, parent, attr_name, all_objects)


def ValueIsJsonObject(value):
    return (isinstance(value, dict) and
            'obj_type' in value)


def ObjectId(obj):
    try:
        ident = obj['id']  # JSON Object
    except Exception:
        try:
            ident = obj.id  # Gnome Object
        except Exception:
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
    '''
    if model_object.__class__.__name__ in FQNamesToDict(obj_types):
        return True

    return False


def RegisterObject(obj, request, implemented_types):
    '''
        Recursively register an object plus all contained child objects.
        Registering means we put the object somewhere it can be looked up
        in the Web API.
        We would mainly like to register PyGnome objects.  Others
        we probably don't care about.
    '''
    sequence_types = (list, tuple, OrderedCollection, SpillContainerPair)

    if (isinstance(obj, implemented_types)):
        set_session_object(obj, request)

    if isinstance(obj, sequence_types):
        for i in obj:
            if (isinstance(i, implemented_types)):
                RegisterObject(i, request, implemented_types)
    elif hasattr(obj, '__dict__'):
        for k in dir(obj):
            attr = getattr(obj, k)
            if (isinstance(attr, implemented_types + sequence_types)):
                RegisterObject(attr, request, implemented_types)


def obj_id_from_url(request):
    '''
        The pyramid URL parser returns a tuple of 0 or more
        matching items, at least when using the * wild card
    '''
    obj_id = request.matchdict.get('obj_id')
    return obj_id[0] if obj_id else None


def obj_id_from_req_payload(json_request):
    return json_request.get('id')


def get_session_dir(request):
    model_dir = request.registry.settings['model_data_dir']
    session_id = request.session.session_id
    session_dir = os.path.join(model_dir, 'session', session_id)

    if os.path.isdir(session_dir) is False:
        os.makedirs(session_dir)

    return session_dir


def get_persistent_dir(request):
    model_dir = request.registry.settings['model_data_dir']
    persistent_dir = os.path.join(model_dir, 'persistent')

    if os.path.isdir(persistent_dir) is False:
        os.makedirs(persistent_dir)

    return persistent_dir


def list_session_dir(request):
    '''
        Purely diagnostic in intent, we simply list the files in our
        session directory.
    '''
    session_dir = get_session_dir(request)

    if os.path.isdir(session_dir) is True:
        # our session folder exists, clean out any files
        for f in os.listdir(session_dir):
            print '\t{}'.format(f)


def clean_session_dir(request):
    session_dir = get_session_dir(request)

    if os.path.isdir(session_dir) is True:
        # our session folder exists, clean out any files
        for f in os.listdir(session_dir):
            try:
                f = os.path.join(session_dir, f)
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
            except Exception:
                pass


def get_file_path(request, json_request=None):
    '''
        take a request/json object and transform it's filename
        attribute into a full path.

        providing the already parsed json will save the need to reprocess
        the json into a dict. if this is already done before calling
        get_file_path passing it along with the request is recommended

        goods: prefix relates to a mounted share between gnome
        and goods uses the goods_dir ini setting

        http or https is a remote file that should be downloaded
        to a temporary directory and the path updated.
        currently should be limited to urls from the goods domain name
        The file will be placed in a session specific directory inside
        model_data_dir
    '''

    goods_dir = request.registry.settings['goods_dir']
    goods_url = request.registry.settings['goods_url']
    session_dir = get_session_dir(request)

    if json_request is None:
        json_request = ujson.loads(request.body)

    if (json_request['filename'][:4] == 'http' and
            json_request['filename'].find(goods_url) != -1):
        resp = urllib2.urlopen(json_request['filename'])

        (_remote_dir, fname) = os.path.split(json_request['filename'])

        with open(os.path.join(session_dir, fname), 'wb') as fh:
            while True:
                data = resp.read(1024 * 1024)

                if len(data) == 0:
                    break
                else:
                    fh.write(data)

        json_request['filename'] = fname

    if json_request['filename'][:6] == 'goods:' and goods_dir != '':
        full_path = os.path.join(goods_dir, json_request['filename'][6:])
    else:
        full_path = os.path.join(session_dir, json_request['filename'])

    return full_path
