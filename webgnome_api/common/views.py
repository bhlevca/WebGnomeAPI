"""
Common Gnome object request handlers.
"""
import json

from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType,
                                    HTTPNotImplemented)

from .helpers import (JSONImplementsOneOf,
                      FQNamesToList,
                      PyClassFromName)

from .common_object import (CreateObject,
                            UpdateObject,
                            ObjectImplementsOneOf,
                            obj_id_from_url,
                            obj_id_from_req_payload,
                            init_session_objects,
                            get_session_object,
                            set_session_object)

cors_policy = {'origins': ('http://0.0.0.0:8080',),
               'credentials': 'true'
               }


def get_object(request, implemented_types):
    '''Returns a Gnome object in JSON.'''
    obj_id = obj_id_from_url(request)
    if not obj_id:
        return get_specifications(request, implemented_types)
    else:
        obj = get_session_object(obj_id, request.session)
        if obj:
            if ObjectImplementsOneOf(obj, implemented_types):
                return obj.serialize()
            else:
                raise HTTPUnsupportedMediaType()
        else:
            raise HTTPNotFound()


def get_specifications(request, implemented_types):
    specs = {}
    for t in implemented_types:
        try:
            name = FQNamesToList((t,))[0][0]
            cls = PyClassFromName(t)
            if cls:
                spec = dict([(n, None)
                             for n in cls._state.get_names(['read', 'update'])
                             ])
                spec['obj_type'] = t
                specs[name] = spec
        except ValueError:
            #print 'failed to get class for {0}'.format(t)
            #print 'error: {0}'.format(e)
            raise
    return specs


def create_object(request, implemented_types):
    '''Creates a Gnome object.'''
    log_prefix = 'req({0}): create_object():'.format(id(request))
    print '>>', log_prefix

    try:
        json_request = json.loads(request.body)
    except:
        raise HTTPBadRequest()

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise HTTPNotImplemented()

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    print log_prefix, 'semaphore acquired...'

    try:
        init_session_objects(request.session)
        obj = CreateObject(json_request, request.session['objects'])
        set_session_object(obj, request.session)
    finally:
        gnome_sema.release()
        print log_prefix, 'semaphore released...'

    print '<<', log_prefix
    return obj.serialize()


def update_object(request, implemented_types):
    '''Updates a Gnome object.'''
    log_prefix = 'req({0}): update_object():'.format(id(request))
    print '>>', log_prefix

    try:
        json_request = json.loads(request.body)
    except:
        raise HTTPBadRequest()

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise HTTPNotImplemented()

    obj = get_session_object(obj_id_from_req_payload(json_request),
                             request.session)
    if obj:
        gnome_sema = request.registry.settings['py_gnome_semaphore']
        gnome_sema.acquire()
        print log_prefix, 'semaphore acquired...'

        try:
            UpdateObject(obj, json_request, request.session['objects'])
            set_session_object(obj, request.session)
        except ValueError as e:
            raise HTTPUnsupportedMediaType(e)
        finally:
            gnome_sema.release()
            print log_prefix, 'semaphore released...'
    else:
        raise HTTPNotFound()

    print '<<', log_prefix
    return obj.serialize()
