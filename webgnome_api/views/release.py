"""
Views for the Release objects.
"""
import ujson
import logging
import zlib
from threading import current_thread
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)
from pyramid.view import view_config
from pyramid.response import Response

from webgnome_api.common.views import (can_persist,
                                       cors_exception,
                                       cors_response,
                                       get_object,
                                       create_object,
                                       cors_policy,
                                       process_upload,
                                       activate_uploaded,
                                       web_ser_opts,
                                       switch_to_existing_session)

from webgnome_api.common.common_object import (CreateObject,
                                               UpdateObject,
                                               ObjectImplementsOneOf,
                                               obj_id_from_url,
                                               obj_id_from_req_payload,
                                               get_file_path)

from webgnome_api.common.session_management import (init_session_objects,
                                                    get_session_objects,
                                                    get_session_object,
                                                    set_session_object,
                                                    acquire_session_lock)

from webgnome_api.common.helpers import JSONImplementsOneOf

from cornice import Service

release = Service(name='release', path='/release*obj_id',
                  description="Release API", cors_policy=cors_policy)

implemented_types = ('gnome.spill.release.PointLineRelease',
                     'gnome.spill.release.SpatialRelease',
                     #'gnome.spill.release.NESDISRelease',
                     'gnome.spill.release.VerticalPlumeRelease',
                     )

log = logging.getLogger(__name__)
geojson_types = ('gnome.spill.release.SpatialRelease',)#, 'gnome.spill.release.NESDISRelease')

@release.get()
def get_release(request):
    '''Returns an Gnome Release object in JSON.'''
    content_requested = request.matchdict.get('obj_id')
    resp = Response(
        content_type='arraybuffer',
        content_encoding='deflate'
    )
    route = content_requested[1] if len(content_requested) > 1 else None
    if (len(content_requested) > 1):
        if route == 'start_positions':
            resp.body = get_start_positions(request)
            return cors_response(request, resp)
        if route == 'polygons':
            resp.body, num_lengths = get_polygons(request)
            resp.headers.add('Access-Control-Expose-Headers', 'num_lengths')
            resp.headers.add('num_lengths', str(num_lengths))
            return cors_response(request, resp)
        if route == 'metadata':
            return get_metadata(request)
    else:
        return get_object(request, implemented_types)

@release.post()
def create_release(request):
    '''Creates a Gnome Release object.'''
    return create_object(request, implemented_types)


@release.put()
def update_release(request):
    '''Updates a Gnome Release object.'''
    return update_object(request, implemented_types)

def get_start_positions(request):
    '''
        Outputs combined SpatialRelease start positions
    '''

    log_prefix = 'req({0}): get_start_positions():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)

        if obj is not None:
            pos = obj.get_start_positions()
            return zlib.compress(pos.astype(np.float32).tobytes())
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)

def get_polygons(request):
    '''
        Outputs the SpatialRelease's Polygons in binary format
    '''
    log_prefix = 'req({0}): get_polygons():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)

        if obj is not None and obj.obj_type in geojson_types:
            lengths, lines = obj.get_polygons()
            lines_bytes = b''.join([l.tobytes() for l in lines])

            return (zlib.compress(lengths.tobytes() + lines_bytes), len(lengths))
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)

def get_metadata(request):
    log_prefix = 'req({0}): get_metadata():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)
        if obj is not None:
            return obj.get_metadata()
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)


@view_config(route_name='release_upload', request_method='OPTIONS')
def release_upload_options(request):
    return cors_response(request, request.response)


@view_config(route_name='release_upload', request_method='POST')
def upload_release(request):
    switch_to_existing_session(request)
    log_prefix = 'req({0}): upload_release():'.format(id(request))
    log.info('>>{}'.format(log_prefix))

    file_list = request.POST.pop('file_list')
    file_list = ujson.loads(file_list)
    name = request.POST.pop('name')
    file_name = file_list

    log.info('  {} file_name: {}, name: {}'
             .format(log_prefix, file_name, name))

    release_type = request.POST.pop('obj_type', [])

    release_json = {'obj_type': release_type,
                    'filename': file_name,
                    'name': name
    }

    release_json.update(request.POST)
    release_json.pop('session')

    request.body = ujson.dumps(release_json).encode('utf-8')

    release_obj = create_release(request)
    resp = Response(ujson.dumps(release_obj))

    log.info('<<{}'.format(log_prefix))
    return cors_response(request, resp)