"""
Common Gnome object request handlers.
"""
import sys
import traceback
import ujson
import shutil
import uuid
import logging
import os
from threading import current_thread

from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPInsufficientStorage,
                                    HTTPUnsupportedMediaType,
                                    HTTPNotImplemented)

from pyramid.interfaces import ISessionFactory

from pyramid.response import FileResponse

from .helpers import (JSONImplementsOneOf,
                      FQNamesToList,
                      PyClassFromName)

from .common_object import (CreateObject,
                            UpdateObject,
                            ObjectImplementsOneOf,
                            obj_id_from_url,
                            obj_id_from_req_payload,
                            get_session_dir,
                            clean_session_dir)

from .session_management import (get_session_objects,
                                 get_session_object,
                                 acquire_session_lock)

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

    req_headers = request.headers.get('Access-Control-Request-Headers')
    if req_headers is not None:
        response.headers.add('Access-Control-Allow-Headers', req_headers)

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

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))

    try:
        log.info('  ' + log_prefix + 'creating ' + json_request['obj_type'])
        obj = CreateObject(json_request, get_session_objects(request))
    except:
        raise cors_exception(request, HTTPUnsupportedMediaType,
                             with_stacktrace=True)
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

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
        session_lock = acquire_session_lock(request)
        log.info('  {} session lock acquired (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

        try:
            UpdateObject(obj, json_request, get_session_objects(request))
        except:
            raise cors_exception(request, HTTPUnsupportedMediaType,
                                 with_stacktrace=True)
        finally:
            session_lock.release()
            log.info('  {} session lock acquired (sess:{}, thr_id: {})'
                     .format(log_prefix, id(session_lock),
                             current_thread().ident))
    else:
        raise cors_exception(request, HTTPNotFound)

    log.info('<<' + log_prefix)
    return obj.serialize()


def process_upload(request, field_name):
    # For some reason, the multipart form does not contain
    # a session cookie, and Nathan so far has not been able to explicitly
    # set it.  So a workaround is to put the session ID in the form as
    # hidden POST content.
    # Then we can re-establish our session with the request after
    # checking that our session id is valid.
    redis_session_id = request.POST['session']
    if redis_session_id in request.session.redis.keys():
        def get_specific_session_id(redis, timeout, serialize, generator,
                                    session_id=redis_session_id):
            return session_id

        factory = request.registry.queryUtility(ISessionFactory)
        request.session = factory(request,
                                  new_session_id=get_specific_session_id)

        if request.session.session_id != redis_session_id:
            raise cors_response(request,
                                HTTPBadRequest('multipart form request '
                                               'could not re-establish session'
                                               ))

    session_dir = get_session_dir(request)
    max_upload_size = eval(request.registry.settings['max_upload_size'])

    log.info('save_file_dir: {0}'.format(session_dir))
    log.info('max_upload_size: {0}'.format(max_upload_size))

    input_file = request.POST[field_name].file

    # split and select last in array incase a path was pathed as the name
    file_name = request.POST[field_name].filename.split(os.path.sep)[-1]
    extension = '.' + file_name.split('.')[-1]
    # add uuid to the file name incase the user accidentaly uploads
    # multiple files with the same name for different objects.
    orig_file_name = file_name
    file_name = file_name.replace(extension,
                                  '-' + str(uuid.uuid4()) + extension)
    file_path = os.path.join(session_dir, file_name)

    # check the size of our incoming file
    input_file.seek(0, 2)
    size = input_file.tell()
    log.info('Incoming file size: {0}'.format(size))

    if size > max_upload_size:
        raise cors_response(request,
                            HTTPBadRequest('file is too big!  Max size = {0}'
                                           .format(max_upload_size)))

    # now we check if we have enough space to save the file.
    if platform.system() == 'Windows':
        fb = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        free_bytes = fb.value / 1024 / 1024
    else:
        stat_vfs = os.statvfs(session_dir)
        free_bytes = stat_vfs.f_bavail * stat_vfs.f_frsize

    if size >= free_bytes:
        raise cors_response(request,
                            HTTPInsufficientStorage('Not enough space '
                                                    'to save the file'))

    # Finally write the data to the session temporary dir
    input_file.seek(0)
    with open(file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    log.info('\tSuccessfully uploaded file "{0}"'.format(file_path))

    return file_path, orig_file_name
