"""
Views for the Mover objects.
This currently includes ??? objects.
"""
import logging

import numpy
np = numpy

from geojson import Feature, FeatureCollection, MultiPolygon

from pyramid.httpexceptions import HTTPNotFound
from cornice import Service

from gnome import basic_types
from gnome.movers.current_movers import CurrentMoversBase

from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy,
                                       cors_exception)

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

            features = []

            if isinstance(mover, CurrentMoversBase):
                signature = get_grid_signature(mover)
                triangle_multipolygon = get_triangle_multipolygon(mover)
                features.append(Feature(geometry=triangle_multipolygon,
                                        id='1',
                                        properties={'signature': signature}))

            return FeatureCollection(features)
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
    points = get_points(mover)

    dtype = points[0].dtype.descr
    raw_points = points.view(dtype='<f8').reshape(-1, len(dtype))
    point_diffs = raw_points[1:] - raw_points[:-1]

    return abs(point_diffs.view(dtype=np.complex)).sum()


def get_triangle_multipolygon(mover):
    '''
        The triangle data that we get from the mover is in the form of
        indices into the points array.
        So we get our triangle data and points array, and then build our
        triangle coordinates by reference.
    '''
    triangle_data = get_triangle_data(mover)
    points = get_points(mover)

    dtype = triangle_data[0].dtype.descr
    unstructured_type = dtype[0][1]
    unstructured = (triangle_data.view(dtype=unstructured_type)
                    .reshape(-1, len(dtype))[:, :3])

    triangles = points[unstructured]

    return MultiPolygon(coordinates=[[t] for t in triangles.tolist()])


def get_triangle_data(mover):
    return mover.mover._get_triangle_data()


def get_points(mover):
    points = (mover.mover._get_points()
              .astype([('long', '<f8'), ('lat', '<f8')]))
    points['long'] /= 10 ** 6
    points['lat'] /= 10 ** 6

    return points


def get_center_points(mover):
    return mover.mover._get_center_points()


def get_velocities(mover):
    return mover.mover._get_velocity_handle()


def get_tide_values(mover, times):
    return mover._tide.cy_obj.get_time_value(times)
