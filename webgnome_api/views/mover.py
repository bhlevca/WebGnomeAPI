"""
Views for the Mover objects.
This currently includes ??? objects.
"""

import logging

from pyramid.httpexceptions import HTTPNotFound
from cornice import Service

from gnome.utilities import time_utils

from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy,
                                       cors_exception)

from webgnome_api.common.session_management import get_active_model

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
                     'gnome.movers.vertical_movers.RiseVelocityMover',
                     )


@mover.get()
def get_mover(request):
    content_requested = request.matchdict.get('obj_id')

    if (len(content_requested) > 1 and
            content_requested[0] == 'current' and
            content_requested[1] == 'geojson'):
        return get_aggregate_current_info(request)
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


def get_aggregate_current_info(request):
    log_prefix = 'req({0}): get_aggregate_current_info():'.format(id(request))
    log.info('>>' + log_prefix)

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    log.info('  ' + log_prefix + 'semaphore acquired...')

    try:
        active_model = get_active_model(request)
        if active_model:
            start = active_model.start_time
            start_seconds = time_utils.date_to_sec(start)
            num_hours = active_model.duration.total_seconds() / 60 / 60

            times = [start_seconds + 3600. * dt
                     for dt in range(int(num_hours))]

            res = []
            for m in active_model.movers:
                if hasattr(m, 'tide') and m.tide is not None:
                    log.info('  {0} adding tide mover {1}'
                             .format(log_prefix, m.name))

                    mover_name = m.name
                    tide_values = m._tide.cy_obj.get_time_value(times)['u']

                    res.append(dict(name=mover_name,
                                    tide_values=tide_values.tolist()))

            return res
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        gnome_sema.release()
        log.info('  ' + log_prefix + 'semaphore released...')

    log.info('<<' + log_prefix)
