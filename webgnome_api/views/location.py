"""
Views for the Location objects.
"""
from os import walk
from os.path import sep, join, isdir, split, basename
from logging import getLogger
from threading import current_thread

from geojson import FeatureCollection, Feature, Point

import ujson
import slugify

from pyramid.httpexceptions import HTTPNotFound, HTTPInternalServerError
from cornice import Service

from gnome.persist import load

from webgnome_api.common.common_object import obj_id_from_url, RegisterObject
from webgnome_api.common.session_management import (init_session_objects,
                                                    set_active_model,
                                                    get_active_model,
                                                    acquire_session_lock)

from webgnome_api.common.views import cors_exception, cors_policy

location_api = Service(name='location', path='/location*obj_id',
                       description="Location API", cors_policy=cors_policy)

log = getLogger(__name__)


@location_api.get()
def get_location(request):
    '''
        Returns a List of Location objects in JSON if no object specified.
    '''
    log.info('location_api.cors_origins_for("get") = {0}'
             .format(location_api.cors_origins_for('get')))

    # first, lets just query that we can get to the data
    locations_dir = request.registry.settings['locations_dir']
    base_len = len(locations_dir.split(sep))
    location_content = []
    location_file_dirs = []

    for (path, _dirnames, filenames) in walk(locations_dir):
        if len(path.split(sep)) == base_len + 1:
            [location_content.append(ujson.load(open(join(path, f), 'r')))
             for f in filenames
             if f == 'compiled.json']

            [location_file_dirs.append(path + "/" + basename(path) + '_save')
             for f in filenames
             if f == 'compiled.json']

    slug = obj_id_from_url(request)
    if slug:
        matching = [(i, c) for i, c in enumerate(location_content)
                    if slugify.slugify_url(c['name']) == slug]
        if matching:
            session_lock = acquire_session_lock(request)
            log.info('  session lock acquired (sess:{}, thr_id: {})'
                     .format(id(session_lock), current_thread().ident))

            try:
                location_file = location_file_dirs[matching[0][0]]
                log.info('load location: {0}'.format(location_file))
                load_location_file(location_file, request)
            except:
                raise cors_exception(request, HTTPInternalServerError,
                                     with_stacktrace=True)
            finally:
                session_lock.release()
                log.info('  session lock released (sess:{}, thr_id: {})'
                         .format(id(session_lock), current_thread().ident))

            return matching[0][1]
        else:
            raise cors_exception(request, HTTPNotFound)
    else:
        features = [Feature(geometry=Point(c['geometry']['coordinates']),
                            properties={'title': c['name'],
                                        'slug': slugify.slugify_url(c['name']),
                                        'content': c['steps']
                                        }
                            )
                    for c in location_content]
        return FeatureCollection(features)


def load_location_file(location_file, request):
    '''
        We would like to merge the current active model into the new model
        created by our location file prior to clearing our session
    '''
    if isdir(location_file):
        active_model = get_active_model(request)

        new_model = load(location_file)
        new_model._cache.enabled = False

        if active_model is not None:
            active_model._map = new_model._map
            active_model._time_step = new_model._time_step
            active_model._num_time_steps = new_model._num_time_steps
            active_model.merge(new_model)
        else:
            active_model = new_model

        name = split(location_file)[1]
        if name != '':
            active_model.name = name

        init_session_objects(request, force=True)

        log.debug("model loaded - begin registering objects")

        from ..views import implemented_types
        RegisterObject(active_model, request, implemented_types)

        set_active_model(request, active_model.id)
