"""
Common Gnome object request handlers.
"""
import sys
import traceback
import ujson
import logging

from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType,
                                    HTTPNotImplemented)

from pyramid.response import FileResponse

from .helpers import (JSONImplementsOneOf,
                      FQNamesToList,
                      PyClassFromName)

from .common_object import (CreateObject,
                            UpdateObject,
                            ObjectImplementsOneOf,
                            obj_id_from_url,
                            obj_id_from_req_payload)

from .session_management import get_session_objects, get_session_object

cors_policy = {'credentials': True
               }

log = logging.getLogger(__name__)


def cors_exception(request, exception_class, with_stacktrace=False):
    depth = 2
    http_exc = exception_class()

    hdr_val = request.headers.get('Origin')
    if hdr_val is not None:
        http_exc.headers.add('Access-Control-Allow-Origin', hdr_val)
        http_exc.headers.add('Access-Control-Allow-Credentials', 'true')

    if with_stacktrace:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        fmt = traceback.format_exception(exc_type, exc_value, exc_traceback)

        http_exc.json_body = ujson.dumps([l.strip() for l in fmt][-depth:])

    return http_exc


def cors_response(request, response):
    hdr_val = request.headers.get('Origin')
    if hdr_val is not None:
        response.headers.add('Access-Control-Allow-Origin', hdr_val)
        response.headers.add('Access-Control-Allow-Credentials', 'true')

    return response


def cors_file_response(request, path):
    file_response = FileResponse(path)

    hdr_val = request.headers.get('Origin')
    if hdr_val is not None:
        file_response.headers.add('Access-Control-Allow-Origin', hdr_val)
        file_response.headers.add('Access-Control-Allow-Credentials', 'true')

    return file_response


def get_object(request, implemented_types):
    '''Returns a Gnome object in JSON.'''
    obj_id = obj_id_from_url(request)
    if not obj_id:
        return get_specifications(request, implemented_types)
    else:
        obj = get_session_object(obj_id, request)
        if obj:
            if ObjectImplementsOneOf(obj, implemented_types):
                return obj.serialize()
            else:
                raise cors_exception(request, HTTPUnsupportedMediaType)
        else:
            raise cors_exception(request, HTTPNotFound)


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
            raise cors_exception(request, HTTPNotImplemented)
    return specs


def create_object(request, implemented_types):
    '''Creates a Gnome object.'''
    log_prefix = 'req({0}): create_object():'.format(id(request))
    log.info('>>' + log_prefix)

    try:
        json_request = ujson.loads(request.body)
    except:
        raise cors_exception(request, HTTPBadRequest)

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise cors_exception(request, HTTPNotImplemented)

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    log.info('  ' + log_prefix + 'semaphore acquired...')

    try:
        log.info('  ' + log_prefix + 'creating ' + json_request['obj_type'])
        obj = CreateObject(json_request, get_session_objects(request))
    except:
        raise cors_exception(request, HTTPUnsupportedMediaType,
                             with_stacktrace=True)
    finally:
        gnome_sema.release()
        log.info('  ' + log_prefix + 'semaphore released...')

    log.info('<<' + log_prefix)
    return obj.serialize()


def update_object(request, implemented_types):
    '''Updates a Gnome object.'''
    log_prefix = 'req({0}): update_object():'.format(id(request))
    log.info('>>' + log_prefix)

    try:
        json_request = ujson.loads(request.body)
    except:
        raise cors_exception(request, HTTPBadRequest)

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise cors_exception(request, HTTPNotImplemented)

    obj = get_session_object(obj_id_from_req_payload(json_request),
                             request)
    if obj:
        gnome_sema = request.registry.settings['py_gnome_semaphore']
        gnome_sema.acquire()
        log.info('  ' + log_prefix + 'semaphore acquired...')

        try:
            UpdateObject(obj, json_request, get_session_objects(request))
        except:
            raise cors_exception(request, HTTPUnsupportedMediaType,
                                 with_stacktrace=True)
        finally:
            gnome_sema.release()
            log.info('  ' + log_prefix + 'semaphore released...')
    else:
        raise cors_exception(request, HTTPNotFound)

    log.info('<<' + log_prefix)
    return obj.serialize()
