"""
Views for the Location objects.
"""
from os import walk
from os.path import sep, join, isdir, split
from logging import getLogger

import ujson
import slugify

from pyramid.httpexceptions import HTTPNotFound, HTTPInternalServerError
from cornice import Service

from gnome.persist import load

from webgnome_api.common.osgeo_helpers import FeatureCollection
from webgnome_api.common.common_object import obj_id_from_url, RegisterObject
from webgnome_api.common.session_management import (init_session_objects,
                                                    set_active_model,
                                                    get_active_model)

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

    for (path, dirnames, filenames) in walk(locations_dir):
        if len(path.split(sep)) == base_len + 1:
            [location_content.append(ujson.load(open(join(path, f), 'r')))
             for f in filenames
             if f == 'compiled.json']

            [location_file_dirs.append(join(path, f[:-12] + '_save'))
             for f in filenames
             if f == 'compiled.json']

    slug = obj_id_from_url(request)
    if slug:
        matching = [(i, c) for i, c in enumerate(location_content)
                    if slugify.slugify_url(c['name']) == slug]
        if matching:
            gnome_sema = request.registry.settings['py_gnome_semaphore']
            gnome_sema.acquire()
            try:
                location_file = location_file_dirs[matching[0][0]]
                log.info('load location: {0}'.format(location_file))
                load_location_file(location_file, request)
            except:
                raise cors_exception(request, HTTPInternalServerError,
                                     with_stacktrace=True)
            finally:
                gnome_sema.release()

            return matching[0][1]
        else:
            raise cors_exception(request, HTTPNotFound)
    else:
        return FeatureCollection(location_content).serialize()


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
            active_model.merge(new_model)
        else:
            active_model = new_model

        name = split(location_file)[1]
        if name != '':
            active_model.name = name

        init_session_objects(request, force=True)
        log.debug("model loaded - begin registering objects")
        RegisterObject(active_model, request)
        set_active_model(request, active_model.id)
