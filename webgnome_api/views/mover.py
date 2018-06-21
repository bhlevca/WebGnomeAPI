"""
Views for the Mover objects.
This currently includes ??? objects.
"""
import os
import logging
import zlib
from threading import current_thread

import ujson

import numpy as np

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from cornice import Service

from gnome.movers.current_movers import CurrentMoversBase
from gnome.movers import PyMover

from ..common.views import (get_object,
                            create_object,
                            update_object,
                            cors_policy,
                            cors_response,
                            cors_exception,
                            process_upload)

from ..common.session_management import (get_session_object,
                                         acquire_session_lock)

log = logging.getLogger(__name__)

mover = Service(name='mover', path='/mover*obj_id', description="Mover API",
                cors_policy=cors_policy)

implemented_types = ('gnome.movers.simple_mover.SimpleMover',
                     'gnome.movers.wind_movers.WindMover',
                     'gnome.movers.random_movers.RandomMover',
                     'gnome.movers.random_movers.RandomVerticalMover',
                     'gnome.movers.current_movers.CatsMover',
                     'gnome.movers.current_movers.ComponentMover',
                     'gnome.movers.py_current_movers.PyCurrentMover',
                     'gnome.movers.py_wind_movers.PyWindMover',
                     'gnome.movers.current_movers.GridCurrentMover',
                     'gnome.movers.current_movers.IceMover',
                     'gnome.movers.vertical_movers.RiseVelocityMover',
                     )


@mover.get()
def get_mover(request):
    content_requested = request.matchdict.get('obj_id')

    route = content_requested[1] if len(content_requested) > 1 else None

    if (route == 'grid'):
        return get_current_info(request)
    elif (route == 'centers'):
        return get_grid_centers(request)
    elif (route == 'vectors'):
        return get_vector_data(request)
    else:
        return get_object(request, implemented_types)


@mover.post()
def create_mover(request):
    '''Creates a Mover object.'''
    return create_object(request, implemented_types)


@mover.put()
def update_mover(request):
    '''Updates a Mover object.'''
    return update_object(request, implemented_types)


@view_config(route_name='mover_upload', request_method='OPTIONS')
def mover_upload_options(request):
    return cors_response(request, request.response)


@view_config(route_name='mover_upload', request_method='POST')
def upload_mover(request):
    log_prefix = 'req({0}): upload_mover():'.format(id(request))
    log.info('>>{}'.format(log_prefix))

    file_name, name = process_upload(request, 'new_mover')
    file_path = file_name.split(os.path.sep)[-1]
    log.info('  {} file_name: {}, name: {}, file_path: {}'
             .format(log_prefix, file_name, name, file_path))

    mover_type = request.POST.get('obj_type', [])

    basic_json = {'obj_type': mover_type,
                  'filename': file_name,
                  'json_': 'webapi',
                  'name': name}

    env_obj_base_json = {'obj_type': 'temp',
                         'name': name,
                         'data_file': file_name,
                         'grid_file': file_name,
                         'json_': 'webapi',
                         'grid': {'obj_type': ('gnome.environment.'
                                               'gridded_objects_base.PyGrid'),
                                  'filename': file_name,
                                  'json_': 'webapi'}
                         }

    wind_json = {'obj_type': 'gnome.environment.wind.Wind',
                 'filename': file_name,
                 'json_': 'webapi',
                 'name': name,
                 'units': 'knots'}

    if ('PyWindMover' in mover_type):
        env_obj_base_json['obj_type'] = ('gnome.environment'
                                         '.environment_objects.GridWind')
        basic_json['wind'] = env_obj_base_json

    if ('PyCurrentMover' in mover_type):
        env_obj_base_json['obj_type'] = ('gnome.environment'
                                         '.environment_objects.GridCurrent')
        basic_json['current'] = env_obj_base_json

    if ('wind_movers.WindMover' in mover_type):
        basic_json['wind'] = wind_json

    request.body = ujson.dumps(basic_json)

    mover_obj = create_mover(request)
    resp = Response(ujson.dumps(mover_obj))

    log.info('<<{}'.format(log_prefix))
    return cors_response(request, resp)


def get_current_info(request):
    '''
        Outputs GNOME current information for a particular current mover
        in a geojson format.
        The output is a collection of Features.
        The Features contain a MultiPolygon
    '''
    log_prefix = 'req({0}): get_current_info():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        mover = get_session_object(obj_id, request)

        if (mover is not None and
                isinstance(mover, (CurrentMoversBase, PyMover))):
            cells = get_cells(mover)

            return cells.reshape(-1, cells.shape[-1]*cells.shape[-2]).tolist()
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
        Outputs GNOME grid centers for a particular mover
    '''

    log_prefix = 'req({0}): get_current_info():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        mover = get_session_object(obj_id, request)

        if (mover is not None and
                isinstance(mover, (CurrentMoversBase, PyMover))):
            centers = get_center_points(mover)

            return centers.tolist()
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)


def get_vector_data(request):
    log_prefix = 'req({0}): get_grid():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)

        if obj is not None:
            log.info('{} found mover of type: {}'
                     .format(log_prefix, obj.__class__))
            vec_data = get_velocities(obj)

            resp = Response(content_type='arraybuffer')

            resp.body, dshape = (zlib.compress(vec_data.tobytes()),
                                 vec_data.shape)

            resp.headers.add('content-encoding', 'deflate')
            resp.headers.add('Access-Control-Expose-Headers', 'shape')
            resp.headers.add('shape', str(dshape))

            return resp
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)


def get_grid_signature(mover):
    '''
        Here we are trying to get an n-dimensional signature of our
        grid data.
        There may be a better way to do this, but for now we will get the
        euclidian distances between all sequential points and sum them.
    '''
    points = mover.get_points()

    dtype = points[0].dtype.descr
    raw_points = points.view(dtype='<f8').reshape(-1, len(dtype))
    point_diffs = raw_points[1:] - raw_points[:-1]

    return abs(point_diffs.view(dtype=np.complex)).sum()


def get_cells(mover):
    grid_data = mover.get_grid_data()
    if not isinstance(mover, PyMover):
        d_t = grid_data.dtype.descr
        u_t = d_t[0][1]
        n_s = grid_data.shape + (len(d_t),)
        grid_data = grid_data.view(dtype=u_t).reshape(*n_s)

    return grid_data
    # return [t for t in grid_data.tolist()]


def get_center_points(mover):
    if hasattr(mover, 'mover'):
        return mover.mover._get_center_points()
    else:
        return mover.get_center_points()


def get_velocities(mover):
    return mover.mover._get_velocity_handle()


def get_tide_values(mover, times):
    return mover._tide.cy_obj.get_time_value(times)
