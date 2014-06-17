"""
Views for the Location objects.
"""
from os import walk
from os.path import sep, join
from collections import OrderedDict

import json
import slugify

from pyramid.httpexceptions import HTTPNotFound
from cornice import Service

from webgnome_api.common.common_object import obj_id_from_url
from webgnome_api.common.views import cors_policy

location_api = Service(name='location', path='/location*obj_id',
                  description="Location API", cors_policy=cors_policy)

# We need to return a feature collection structure on a get with no
# id specified
#  {"type": "FeatureCollection",
#   "features": [{"type": "Feature",
#                 "properties": {"title": "Long Island Sound",
#                                "slug": "long_island_sound",
#                                "content": "History about Long Island Sound."
#                                },
#                 "geometry": {"type": "Point",
#                              "coordinates": [-72.879489, 41.117006]
#                              }
#                 },
#                 ...
#                 ]
#  }


@location_api.get()
def get_location(request):
    '''
        Returns a List of Location objects in JSON if no object specified.
    '''
    # first, lets just query that we can get to the data
    locations_dir = get_locations_dir_from_config(request)
    base_len = len(locations_dir.split(sep))
    location_content = []

    for (path, dirnames, filenames) in walk(locations_dir):
        if len(path.split(sep)) == base_len + 1:
            [location_content.append(json.load(open(join(path, f), 'r'),
                                               object_pairs_hook=OrderedDict))
             for f in filenames
             if f[-12:] == '_wizard.json']

    slug = obj_id_from_url(request)
    if slug:
        matching = [b for b in location_content
                    if slugify.slugify_url(b['name']) == slug]
        if matching:
            return matching[0]
        else:
            return HTTPNotFound()
        pass
    else:
        return FeatureCollection(location_content).serialize()


class Feature(object):
    def __init__(self, json_body):
        self.type = 'Feature'
        self.json_body = json_body

    @property
    def properties(self):
        return dict(title=self.json_body['name'],
                    slug=slugify.slugify_url(self.json_body['name']),
                    content='???')

    @property
    def geometry(self):
        return dict(type='Point',
                    coordinates=self.json_body['coords'])

    def serialize(self):
        return dict(type='Feature',
                    properties=self.properties,
                    geometry=self.geometry)


class FeatureCollection(object):
    def __init__(self, json_list):
        self.type = 'FeatureCollection'
        self.features = []
        for b in json_list:
            self.features.append(Feature(b))

    def serialize(self):
        return dict(type='FeatureCollection',
                    features=[f.serialize() for f in self.features])


def get_locations_dir_from_config(request):
    map_dir = request.registry.settings['locations_dir']
    if map_dir[0] == sep:
        full_path = map_dir
    else:
        here = request.registry.settings['install_path']
        full_path = join(here, map_dir)
    return full_path
