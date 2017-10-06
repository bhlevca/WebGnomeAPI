"""
Views for the Model object.
"""
import logging
from threading import current_thread

import ujson

from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType,
                                    HTTPNotImplemented)
from cornice import Service

from webgnome_api.common.views import (cors_exception,
                                       cors_policy,
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
                                                    acquire_session_lock,
                                                    get_active_model,
                                                    set_active_model)

from webgnome_api.common.helpers import JSONImplementsOneOf

from gnome.model import Model


log = logging.getLogger(__name__)

model = Service(name='model', path='/model*obj_id', description="Model API",
                cors_policy=cors_policy)

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
    session_lock = acquire_session_lock(request)
    log.info('  session lock acquired (sess:{}, thr_id: {})'
             .format(id(session_lock), current_thread().ident))

    try:
        if not obj_id:
            my_model = get_active_model(request)
            if my_model:
                ret = my_model.serialize()
            else:
                ret = get_specifications(request, implemented_types)
        else:
            obj = get_session_object(obj_id, request)
            if obj:
                if ObjectImplementsOneOf(obj, implemented_types):
                    set_active_model(request, obj.id)
                    ret = obj.serialize()
                else:
                    # we refer to an object, but it is not a Model
                    raise cors_exception(request, HTTPBadRequest)
            else:
                raise cors_exception(request, HTTPNotFound)
    finally:
        session_lock.release()
        log.info('  session lock released (sess:{}, thr_id: {})'
                 .format(id(session_lock), current_thread().ident))

    return ret


@model.post()
def create_model(request):
    '''
        Creates a new model
    '''
    log_prefix = 'req({0}): create_object():'.format(id(request))
    log.info('>>' + log_prefix)

    try:
        json_request = ujson.loads(request.body)
    except Exception:
        json_request = None

    if json_request and not JSONImplementsOneOf(json_request,
                                                implemented_types):
        raise cors_exception(request, HTTPNotImplemented)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))

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
    except Exception:
        raise cors_exception(request, HTTPUnsupportedMediaType,
                             with_stacktrace=True)
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)
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
    log_prefix = 'req({0}): update_model():'.format(id(request))
    log.info('>>' + log_prefix)

    ret = None
    try:
        json_request = ujson.loads(request.body)
    except Exception:
        raise cors_exception(request, HTTPBadRequest)

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise cors_exception(request, HTTPNotImplemented)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))

    obj_id = obj_id_from_req_payload(json_request)
    if obj_id:
        active_model = get_session_object(obj_id, request)
    else:
        active_model = get_active_model(request)

    if active_model:
        try:
            if UpdateObject(active_model, json_request,
                            get_session_objects(request)):
                set_session_object(active_model, request)
            ret = active_model.serialize()
        except Exception:
            raise cors_exception(request, HTTPUnsupportedMediaType,
                                 with_stacktrace=True)
        finally:
            session_lock.release()
            log.info('  ' + log_prefix + 'session lock released...')
    else:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

        msg = ("raising cors_exception() in update_model. "
               "Updating model before it exists.")
        log.warning('  ' + log_prefix + msg)

        raise cors_exception(request, HTTPNotFound)

    log.info('<<' + log_prefix)
    return ret
