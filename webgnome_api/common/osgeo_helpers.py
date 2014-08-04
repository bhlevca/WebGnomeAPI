'''
Helper functions to make it a little easier to use the
Geospatial Data Abstraction Libraries (GDAL/OGR).
'''
import slugify

from osgeo import gdal, ogr


# We need to return a feature collection structure on a get with no
# id specified
#  {"type": "FeatureCollection",
#   "features": [{"type": "Feature",
#                 "properties": {"title": "Long Island Sound",
#                                "slug": "long_island_sound",
#                                "content": "History about Long Island Sound"},
#                 "geometry": {"type": "Point",
#                              "coordinates": [-72.879489, 41.117006]}
#                 },
#                 ...
#                 ]
#  }
class Feature(object):
    def __init__(self, json_body):
        self.type = 'Feature'
        self.json_body = json_body

    @property
    def properties(self):
        res = dict(content='???')

        if 'properties' in self.json_body:
            res.update(self.json_body['properties'])

        if 'name' in self.json_body:
            res['title'] = self.json_body['name']
            res['slug'] = slugify.slugify_url(self.json_body['name'])

        return res

    @property
    def geometry(self):
        geo = {}
        if 'geometry' in self.json_body:
            geo = self.json_body['geometry']

        return dict(type=geo.get('type', 'Point'),
                    coordinates=geo['coordinates'])

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


def ogr_drivers():
    return [ogr.GetDriver(i) for i in range(ogr.GetDriverCount())]


def ogr_driver_names():
    return [d.GetName() for d in ogr_drivers()]


def ogr_open_file(filename):
    return ogr.Open(filename)


def ogr_layers(infile):
    return [infile.GetLayerByIndex(i) for i in range(infile.GetLayerCount())]


def ogr_features(layer):
    layer.SetNextByIndex(0)
    return [feature for feature in layer]
