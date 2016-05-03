"""
Views for the Mover objects.
This currently includes ??? objects.
"""
import logging
import ujson
import os
import numpy as np

from geojson import Feature, FeatureCollection, MultiPolygon, Polygon

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from cornice import Service

from gnome import basic_types
from gnome.movers.current_movers import CurrentMoversBase

from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy,
                                       cors_response,
                                       cors_exception,
                                       process_upload)

from webgnome_api.common.session_management import get_session_object

log = logging.getLogger(__name__)

mover = Service(name='mover', path='/mover*obj_id', description="Mover API",
                cors_policy=cors_policy)

implemented_types = ('gnome.movers.simple_mover.SimpleMover',
                     'gnome.movers.wind_movers.WindMover',
                     'gnome.movers.wind_movers.GridWindMover',
                     'gnome.movers.random_movers.RandomMover',
                     'gnome.movers.random_movers.RandomVerticalMover',
                     'gnome.movers.current_movers.CatsMover',
                     'gnome.movers.current_movers.ComponentMover',
                     'gnome.movers.current_movers.GridCurrentMover',
                     'gnome.movers.current_movers.IceMover',
                     'gnome.movers.vertical_movers.RiseVelocityMover',
                     )


@mover.get()
def get_mover(request):
    content_requested = request.matchdict.get('obj_id')

    if (len(content_requested) > 1 and
            content_requested[1] == 'grid'):
        return get_current_info(request)
    elif (len(content_requested) > 1 and 
            content_requested[1] == 'centers'):
        return get_grid_centers(request)
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
    file_path = process_upload(request, 'new_mover')
    resp = Response(ujson.dumps({'filename': file_path}))

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

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    log.info('  {0} {1}'.format(log_prefix, 'semaphore acquired...'))

    try:
        obj_id = request.matchdict.get('obj_id')[0]
        mover = get_session_object(obj_id, request)

        if mover is not None:
            # start = active_model.start_time
            # start_seconds = time_utils.date_to_sec(start)
            # num_hours = active_model.duration.total_seconds() / 60 / 60
            #
            # times = [start_seconds + 3600. * dt
            #          for dt in range(int(num_hours))]

            if isinstance(mover, CurrentMoversBase):
                # signature = get_grid_signature(mover)
                cells = get_cells(mover)

            return cells.reshape(-1, cells.shape[-1]*cells.shape[-2]).tolist()
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        gnome_sema.release()
        log.info('  ' + log_prefix + 'semaphore released...')

    log.info('<<' + log_prefix)

def get_grid_centers(request):
    '''
        Outputs GNOME grid centers for a particular mover
    '''
    log_prefix = 'req({0}): get_current_info():'.format(id(request))
    log.info('>>' + log_prefix)

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    log.info('  {0} {1}'.format(log_prefix, 'semaphore acquired...'))

    try:
        obj_id = request.matchdict.get('obj_id')[0]
        mover = get_session_object(obj_id, request)

        if mover is not None:
            
            if isinstance(mover, CurrentMoversBase):
                # signature = get_grid_signature(mover)
                centers = get_center_points(mover)

            return centers.tolist()
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        gnome_sema.release()
        log.info('  ' + log_prefix + 'semaphore released...')

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
    d_t = grid_data.dtype.descr
    u_t = d_t[0][1]
    n_s = grid_data.shape + (len(d_t),)
    grid_data = grid_data.view(dtype = u_t).reshape(*n_s)
    return grid_data
    # return [t for t in grid_data.tolist()]


def get_center_points(mover):
    return mover.mover._get_center_points()


def get_velocities(mover):
    return mover.mover._get_velocity_handle()


def get_tide_values(mover, times):
    return mover._tide.cy_obj.get_time_value(times)
