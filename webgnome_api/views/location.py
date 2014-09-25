"""
Views for the Location objects.
"""
from os import walk
from os.path import sep, join, isdir
from collections import OrderedDict
from types import MethodType, FunctionType

import json
import slugify

from pyramid.httpexceptions import HTTPNotFound
from cornice import Service

from gnome.utilities.orderedcollection import OrderedCollection
from gnome.spill_container import SpillContainerPair
from gnome.persist import load

from webgnome_api.common.osgeo_helpers import (FeatureCollection,)

from webgnome_api.common.common_object import obj_id_from_url

from webgnome_api.common.session_management import (init_session_objects,
                                                    set_session_object,
                                                    set_active_model)

from webgnome_api.common.views import cors_exception, cors_policy

location_api = Service(name='location', path='/location*obj_id',
                  description="Location API", cors_policy=cors_policy)


@location_api.get()
def get_location(request):
    '''
        Returns a List of Location objects in JSON if no object specified.
    '''
    # first, lets just query that we can get to the data
    locations_dir = get_locations_dir_from_config(request)
    base_len = len(locations_dir.split(sep))
    location_content = []
    location_file_dirs = []

    for (path, dirnames, filenames) in walk(locations_dir):
        if len(path.split(sep)) == base_len + 1:
            [location_content.append(json.load(open(join(path, f), 'r'),
                                               object_pairs_hook=OrderedDict))
             for f in filenames
             if f[-12:] == '_wizard.json']
            [location_file_dirs.append(join(path, f[:-12] + '_save'))
             for f in filenames
             if f[-12:] == '_wizard.json']

    slug = obj_id_from_url(request)
    if slug:
        matching = [(i, c) for i, c in enumerate(location_content)
                    if slugify.slugify_url(c['name']) == slug]
        if matching:
            gnome_sema = request.registry.settings['py_gnome_semaphore']
            gnome_sema.acquire()
            try:
                location_file = location_file_dirs[matching[0][0]]
                load_location_file(location_file, request)
            finally:
                gnome_sema.release()

            return matching[0][1]
        else:
            raise cors_exception(request, HTTPNotFound)
    else:
        return FeatureCollection(location_content).serialize()


def get_locations_dir_from_config(request):
    map_dir = request.registry.settings['locations_dir']
    if map_dir[0] == sep:
        full_path = map_dir
    else:
        here = request.registry.settings['install_path']
        full_path = join(here, map_dir)
    return full_path


def load_location_file(location_file, request):
    if isdir(location_file):
        init_session_objects(request, force=True)
        obj = load(location_file)
        RegisterObject(obj, request)
        set_active_model(request, obj.id)


def RegisterObject(obj, request):
    '''
        Recursively register an object plus all contained child objects.
        Registering means we put the object somewhere it can be looked up
        in the Web API.
        We would mainly like to register PyGnome objects.  Others
        we probably don't care about.
    '''
    if (hasattr(obj, 'id')
        and not obj.__class__.__name__ == 'type'):
        print 'RegisterObjects(): registering:', (obj.__class__.__name__,
                                                  obj.id)
        set_session_object(obj, request)
    if isinstance(obj, (list, tuple, OrderedCollection,
                        SpillContainerPair)):
        for i in obj:
            RegisterObject(i, request)
        pass
    elif hasattr(obj, '__dict__'):
        for k in dir(obj):
            attr = getattr(obj, k)
            if not (k.find('_') == 0
                    or isinstance(attr, (MethodType, FunctionType))):
                RegisterObject(attr, request)
