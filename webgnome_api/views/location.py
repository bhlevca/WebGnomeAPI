"""
Views for the Location objects.
"""
from os import listdir, walk
from os.path import sep, isfile, isdir, join

import json

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType,
                                    HTTPNotImplemented)

from webgnome_api.common.views import (get_object,
                                       cors_policy)

from webgnome_api.common.common_object import (CreateObject,
                                               UpdateObject,
                                               obj_id_from_req_payload,
                                               init_session_objects,
                                               get_session_object,
                                               set_session_object)

from webgnome_api.common.helpers import JSONImplementsOneOf

location_api = Service(name='location', path='/location*obj_id',
                  description="Location API", cors_policy=cors_policy)

#implemented_types = ('gnome.map.MapFromBNA',
#                     )


@location_api.get()
def get_location(request):
    '''
        Returns a List of Location objects in JSON if no object specified.
    '''
    # first, lets just query that we can get to the data
    locations_dir = get_locations_dir_from_config(request)
    base_len = len(locations_dir.split(sep))
    print 'num path components:', base_len
    res = []

    for (path, dirnames, filenames) in walk(locations_dir):
        if len(path.split(sep)) == base_len + 1:
            filenames = [f for f in filenames if f[-12:] == '_wizard.json']
            [res.append(json.load(open(join(path, f), 'r')))
             for f in filenames]

    return res


#{"type": "FeatureCollection",
# "features": [{"type": "Feature",
#               "properties": {"title": "Long Island Sound",
#                              "content": "History about Long Island Sound.",
#                              "slug": "long_island_sound"
#                              },
#               "geometry": {"type": "Point",
#                            "coordinates": [-72.879489, 41.117006]
#                            }
#               }]
#}
class Feature(object):
    def __init__(self, filename):
        self.type = 'Feature'
        self.json_body = json.load(open(filename, 'r'))
        self.properties = self.properties_from_json()

    def properties_from_json(self):
        ret = dict(title=self.json_body['name'],
                   content=self
                   )


class FeatureCollection(object):
    def __init__(self, filename):
        self.type = 'FeatureCollection'
        self.features = []
        self.features.append(Feature(filename))


def get_locations_dir_from_config(request):
    map_dir = request.registry.settings['locations_dir']
    if map_dir[0] == sep:
        full_path = map_dir
    else:
        here = request.registry.settings['here']
        full_path = join(here, map_dir)
    return full_path
