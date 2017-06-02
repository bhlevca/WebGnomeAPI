"""
Views for the Environment objects.
This currently includes Wind and Tide objects.
"""
import ujson
import os
import logging
import zlib
import numpy as np
from threading import current_thread

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from gnome.environment.environment_objects import GridCurrent
from gnome.environment.gridded_objects_base import Grid_U

from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy,
                                       cors_response,
                                       cors_exception,
                                       process_upload)

from cornice import Service

from ..common.session_management import (get_session_object,
                                         acquire_session_lock)
log = logging.getLogger(__name__)

env = Service(name='environment', path='/environment*obj_id',
              description="Environment API",
              cors_policy=cors_policy, accept=['application/json', 'application/octet-stream'], content_type=['application/json', 'binary'])

implemented_types = ('gnome.environment.Tide',
                     'gnome.environment.Wind',
                     'gnome.environment.Water',
                     'gnome.environment.Waves',
                     'gnome.environment.environment_objects.GridCurrent',
                     )


@env.get()
def get_environment(request):
    '''Returns an Gnome Environment object in JSON.'''
    content_requested = request.matchdict.get('obj_id')
#     import pytest
#     pytest.set_trace()
    resp = Response(content_type='arraybuffer')
    if (len(content_requested) > 1):
        if content_requested[1] == 'grid':
            resp.body = get_grid(request)
            resp.headers.add('content-encoding', 'deflate')
            return cors_response(request, resp)
        if content_requested[1] == 'data':
            return get_grid_centers(request)
        return get_object(request, implemented_types)


@env.post()
def create_environment(request):
    '''Creates an Environment object.'''
    return create_object(request, implemented_types)


@env.put()
def update_environment(request):
    '''Updates an Environment object.'''
    return update_object(request, implemented_types)


@view_config(route_name='environment_upload', request_method='OPTIONS')
def environment_upload_options(request):
    return cors_response(request, request.response)


@view_config(route_name='environment_upload', request_method='POST')
def environment_upload(request):
    filename, name = process_upload(request, 'new_environment')
    resp = Response(ujson.dumps({'filename': filename, 'name': name}))

    return cors_response(request, resp)

def get_grid(request):
    '''
        Outputs a subset of the object's dataset in binary format
    '''
    log_prefix = 'req({0}): get_grid():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)

        if obj is not None and isinstance(obj, (GridCurrent,)):
            cells = get_cells(obj)

            return zlib.compress(cells.reshape(-1, cells.shape[-1]*cells.shape[-2]).astype(np.float64).tobytes())
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)


def get_grid_centers(request):
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

        if obj is not None and isinstance(obj, (CurrentMoversBase, GridWindMover, PyMover)):
            centers = get_center_points(obj)

            return centers.tolist()
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)


def get_grid_signature(obj):
    '''
        Here we are trying to get an n-dimensional signature of our
        grid data.
        There may be a better way to do this, but for now we will get the
        euclidian distances between all sequential points and sum them.
    '''
    points = obj.get_points()

    dtype = points[0].dtype.descr
    raw_points = points.view(dtype='<f8').reshape(-1, len(dtype))
    point_diffs = raw_points[1:] - raw_points[:-1]

    return abs(point_diffs.view(dtype=np.complex)).sum()


def get_cells(obj):
    grid_data = None
    grid_data = obj.grid.get_cells()
#     if isinstance(obj.grid, Grid_U):
#         grid_data = obj.grid.nodes[obj.grid.faces[:]]
#     else:
#         grid_data = obj.grid.get_cells()
# #         import pdb
# #         pdb.set_trace()
# #         lons = obj.grid.node_lon[:]
# #         lats = obj.grid.node_lat[:]
# #         grid_data = np.column_stack((lons.reshape(-1), lats.reshape(-1)))
    return grid_data
