"""
Views for the Environment objects.
This currently includes Wind and Tide objects.
"""
import ujson
import logging
import zlib
import numpy as np
from threading import current_thread

from pyramid.settings import asbool
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPNotImplemented

from gnome.environment.environment_objects import GridCurrent, GridWind

from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy,
                                       cors_response,
                                       cors_exception,
                                       process_upload,
                                       can_persist,
                                       activate_uploaded)

from cornice import Service

from ..common.session_management import (get_session_object,
                                         acquire_session_lock)
log = logging.getLogger(__name__)

grid = Service(name='environment/grid', path='/grid*obj_id',
               description="Grid API",
               cors_policy=cors_policy,
               content_type=['application/json', 'binary'])

implemented_types = ('gnome.environment.gridded_objects_base.Grid_U',
                     'gnome.environment.gridded_objects_base.Grid_R',
                     'gnome.environment.gridded_objects_base.Grid_S',
                     )

@grid.get()
def get_grid(request):
    '''Returns an Grid object in JSON.'''
    content_requested = request.matchdict.get('obj_id')
    resp = Response(
        content_type='arraybuffer',
        content_encoding='deflate'
    )
    route = content_requested[1] if len(content_requested) > 1 else None
    if (len(content_requested) > 1):
        if route == 'lines':
            resp.body, num_lengths = get_lines(request)
            resp.headers.add('Access-Control-Expose-Headers', 'num_lengths')
            resp.headers.add('num_lengths', str(num_lengths))
            return cors_response(request, resp)
        if route == 'nodes':
            resp.body = get_nodes(request)
            return cors_response(request, resp)
        if route == 'centers':
            resp.body = get_centers(request)
            return cors_response(request, resp)
        if route == 'metadata':
            return get_metadata(request)
    else:
        return get_object(request, implemented_types)


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


def get_lines(request):
    '''
    Outputs the object's grid lines in binary format
    '''
    log_prefix = 'req({0}): get_grid():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)

        if obj is not None:
            lengths, lines = obj.get_lines()
            lines_bytes = ''.join([l.tobytes() for l in lines])

            return (zlib.compress(lengths.tobytes() + lines_bytes), len(lengths))
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)


def get_centers(request):
    '''
        Outputs GNOME grid centers for a particular obj
    '''

    log_prefix = 'req({0}): get_current_info():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)

        if obj is not None:
            centers = obj.get_centers()
            return zlib.compress(centers.astype(np.float32).tobytes())
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)


def get_nodes(request):
    '''
        Outputs the object's grid nodes in binary format
    '''
    log_prefix = 'req({0}): get_grid():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)

        if obj is not None:
            nodes = obj.get_nodes()

            return zlib.compress(nodes.astype(np.float32).tobytes())
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)
