"""
Views for the Model object.
"""
import sys
import traceback

import json
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType,
                                    HTTPNotImplemented)
from cornice import Service

from webgnome_api.common.views import (cors_policy,
                                       get_specifications)
from webgnome_api.common.common_object import (CreateObject,
                                               UpdateObject,
                                               ObjectImplementsOneOf,
                                               obj_id_from_url,
                                               obj_id_from_req_payload)

from webgnome_api.common.session_management import (init_session_objects,
                                                    get_session_objects,
                                                    get_session_object,
                                                    set_session_object,
                                                    get_active_model,
                                                    set_active_model)

from webgnome_api.common.helpers import JSONImplementsOneOf

model = Service(name='model', path='/model*obj_id', description="Model API",
                cors_policy=cors_policy)

import gnome
from gnome.model import Model
implemented_types = ('gnome.model.Model',
                     )


@model.get()
def get_model(request):
    '''
        Returns Model object in JSON.
        - This method varies slightly from the common object method in that
          if we don't specify a model ID, we:
          - return the current active model if it exists or...
          - return the specification.
    '''
    ret = None
    obj_id = obj_id_from_url(request)
    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()

    if not obj_id:
        my_model = get_active_model(request)
        if my_model:
            ret = my_model.serialize()
        else:
            # - return a Model specification
            ret = get_specifications(request, implemented_types)
    else:
        obj = get_session_object(obj_id, request)
        if obj:
            if ObjectImplementsOneOf(obj, implemented_types):
                set_active_model(request, obj.id)
                ret = obj.serialize()
            else:
                raise HTTPUnsupportedMediaType()
        else:
            raise HTTPNotFound()

    gnome_sema.release()
    return ret


@model.post()
def create_model(request):
    '''
        Creates a new model
    '''
    log_prefix = 'req({0}): create_object():'.format(id(request))
    print '>>', log_prefix

    try:
        json_request = json.loads(request.body)
    except:
        json_request = None

    if json_request and not JSONImplementsOneOf(json_request,
                                                implemented_types):
        raise HTTPNotImplemented()

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    print '  ', log_prefix, 'semaphore acquired...'

    try:
        init_session_objects(request, force=True)
        if json_request:
            new_model = CreateObject(json_request,
                                     get_session_objects(request))
        else:
            new_model = Model()
        set_session_object(new_model, request)
        set_session_object(new_model._map, request)
        set_active_model(request, new_model.id)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        fmt = traceback.format_exception(exc_type, exc_value,
                                         exc_traceback)

        http_exc = HTTPUnsupportedMediaType()

        hdr_val = request.headers.get('Origin')
        if hdr_val != None:
            http_exc.headers.add('Access-Control-Allow-Origin', hdr_val)
            http_exc.headers.add('Access-Control-Allow-Credentials', 'true')

        http_exc.json_body = json.dumps([l.strip() for l in fmt][-2:])

        raise http_exc
    finally:
        gnome_sema.release()
        print '  ', log_prefix, 'semaphore released...'

    print '<<', log_prefix
    return new_model.serialize()


@model.put()
def update_model(request):
    '''
        Returns Model object in JSON.
        - This method varies slightly from the common object method in that
          if we don't specify a model ID, we:
          - update the current active model if it exists or...
          - generate a 'Not Found' exception.
    '''
    ret = None
    try:
        json_request = json.loads(request.body)
    except:
        raise HTTPBadRequest()

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise HTTPNotImplemented()

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()

    obj_id = obj_id_from_req_payload(json_request)
    if obj_id:
        my_model = get_session_object(obj_id, request)
    else:
        my_model = get_active_model(request)

    if my_model:
        try:
            if UpdateObject(my_model, json_request,
                            get_session_objects(request)):
                set_session_object(my_model, request)
            ret = my_model.serialize()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            fmt = traceback.format_exception(exc_type, exc_value,
                                             exc_traceback)

            http_exc = HTTPUnsupportedMediaType()

            hdr_val = request.headers.get('Origin')
            if hdr_val != None:
                http_exc.headers.add('Access-Control-Allow-Origin', hdr_val)
                http_exc.headers.add('Access-Control-Allow-Credentials', 'true')

            http_exc.json_body = json.dumps([l.strip() for l in fmt][-2:])

            raise http_exc
        finally:
            gnome_sema.release()
    else:
        gnome_sema.release()
        raise HTTPNotFound()

    return ret
