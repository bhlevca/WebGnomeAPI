"""
Views for the Map objects.
"""
import os
import json

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType,
                                    HTTPNotImplemented)

from webgnome_api.common.osgeo_helpers import (ogr_open_file,
                                               ogr_layers,
                                               ogr_features,
                                               FeatureCollection)

from webgnome_api.common.views import (get_object,
                                       cors_policy)

from webgnome_api.common.common_object import (CreateObject,
                                               UpdateObject,
                                               ObjectImplementsOneOf,
                                               obj_id_from_url,
                                               obj_id_from_req_payload)

from webgnome_api.common.session_management import (init_session_objects,
                                                    get_session_objects,
                                                    get_session_object,
                                                    set_session_object)

from webgnome_api.common.helpers import JSONImplementsOneOf

map_api = Service(name='map', path='/map*obj_id',
                  description="Map API", cors_policy=cors_policy)

implemented_types = ('gnome.map.MapFromBNA',
                     'gnome.map.GnomeMap'
                     )


@map_api.get()
def get_map(request):
    '''Returns a Gnome Map object in JSON.'''
    obj_ids = request.matchdict.get('obj_id')
    if (len(obj_ids) >= 2 and
        obj_ids[1] == 'geojson'):
        return get_geojson(request, implemented_types)
    else:
        return get_object(request, implemented_types)


@map_api.post()
def create_map(request):
    '''Creates a Gnome Map object.'''
    init_session_objects(request)
    try:
        json_request = json.loads(request.body)
    except:
        raise HTTPBadRequest()

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise HTTPNotImplemented()

    # TODO: should we tie our data directory to the installation path?
    #       or should we be more flexible?
    map_dir = get_map_dir_from_config(request)
    json_request['filename'] = os.path.join(map_dir, json_request['filename'])

    obj = CreateObject(json_request, get_session_objects(request))

    set_session_object(obj, request)
    return obj.serialize()


@map_api.put()
def update_map(request):
    '''Updates a Gnome Map object.'''
    try:
        json_request = json.loads(request.body)
    except:
        raise HTTPBadRequest()

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise HTTPNotImplemented()

    obj = get_session_object(obj_id_from_req_payload(json_request),
                             request)
    if obj:
        try:
            UpdateObject(obj, json_request, get_session_objects(request))
        except ValueError as e:
            raise HTTPUnsupportedMediaType(e)
    else:
        raise HTTPNotFound()

    set_session_object(obj, request)
    return obj.serialize()


def get_geojson(request, implemented_types):
    '''Returns the GeoJson for a Gnome Map object.'''
    obj_id = obj_id_from_url(request)

    obj = get_session_object(obj_id, request)
    if obj:
        if ObjectImplementsOneOf(obj, implemented_types):
            # Here is where we extract the GeoJson from our map object.
            map_file = ogr_open_file(obj.filename)
            bounds_features = []
            shoreline_features = []
            spillarea_features = []

            for layer in ogr_layers(map_file):
                for f in ogr_features(layer):
                    primary_id = f.GetFieldAsString('Primary ID')

                    if primary_id == 'SpillableArea':
                        spillarea_features.append(json.loads(f.ExportToJson()))
                    elif primary_id == 'Map Bounds':
                        bounds_features.append(json.loads(f.ExportToJson()))
                    else:
                        shoreline_features.append(json.loads(f.ExportToJson()))

            return FeatureCollection(shoreline_features).serialize()
        else:
            raise HTTPNotImplemented()
    else:
        raise HTTPNotFound()


def get_map_dir_from_config(request):
    map_dir = request.registry.settings['model_data_dir']
    if map_dir[0] == os.path.sep:
        full_path = map_dir
    else:
        here = request.registry.settings['here']
        full_path = os.path.join(here, map_dir)
    return full_path
