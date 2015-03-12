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

from webgnome_api.common.views import (cors_exception,
                                       get_object,
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
    log_prefix = 'req({0}): create_object():'.format(id(request))

    init_session_objects(request)
    try:
        json_request = json.loads(request.body)
    except:
        raise cors_exception(request, HTTPBadRequest)

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise cors_exception(request, HTTPNotImplemented)

    # TODO: should we tie our data directory to the installation path?
    #       or should we be more flexible?
    if 'filename' in json_request:
        map_dir = get_map_dir_from_config(request)
        json_request['filename'] = os.path.join(map_dir,
                                                json_request['filename'])

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    print '  ', log_prefix, 'semaphore acquired...'

    try:
        obj = CreateObject(json_request, get_session_objects(request))
    except:
        raise cors_exception(request, HTTPUnsupportedMediaType,
                             with_stacktrace=True)
    finally:
        gnome_sema.release()
        print '  ', log_prefix, 'semaphore released...'

    set_session_object(obj, request)
    return obj.serialize()


@map_api.put()
def update_map(request):
    '''Updates a Gnome Map object.'''
    try:
        json_request = json.loads(request.body)
    except:
        raise cors_exception(request, HTTPBadRequest)

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise cors_exception(request, HTTPNotImplemented)

    obj = get_session_object(obj_id_from_req_payload(json_request),
                             request)
    if obj:
        try:
            UpdateObject(obj, json_request, get_session_objects(request))
        except:
            raise cors_exception(request, HTTPUnsupportedMediaType,
                                 with_stacktrace=True)
    else:
        raise cors_exception(request, HTTPNotFound)

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
            shoreline_geo = ''

            for layer in ogr_layers(map_file):
                for f in ogr_features(layer):
                    primary_id = f.GetFieldAsString('Primary ID')

                    # robust but slow solution ~ 1 second processing time
                    # if primary_id == 'SpillableArea':
                    #     spillarea_features.append(json.loads(f.ExportToJson()))
                    # elif primary_id == 'Map Bounds':
                    #     bounds_features.append(json.loads(f.ExportToJson()))
                    # else:
                    #     shoreline_features.append(json.loads(f.ExportToJson()))
                    #     shoreline_geo.append(json.loads(f.GetGeometryRef().ExportToJson())['coordinates'][0])

                    # only doing what we need at the moment
                    # in the future we might need the other layers
                    if primary_id != 'SpillableArea' and primary_id != 'Map Bounds':
                        geom_json = f.GetGeometryRef().ExportToJson()
                        geom_json = geom_json.replace('{ "type": "MultiPolygon", "coordinates": [' , '')
                        geom_json = geom_json.replace('] }', '')
                        shoreline_geo += geom_json + ', ';

            # remove last comma from geometry
            shoreline_geo = shoreline_geo[0:-2]

            json_body = '{\
                "properties": {\
                    "name": "Shoreline"\
                },\
                "geometry": {\
                    "type": "MultiPolygon",\
                    "coordinates": [' + shoreline_geo + ']\
                }\
            }'
            shoreline_feature = json.loads(json_body);
            return FeatureCollection([shoreline_feature]).serialize()
        else:
            raise cors_exception(request, HTTPNotImplemented)
    else:
        raise cors_exception(request, HTTPNotFound)


def get_map_dir_from_config(request):
    map_dir = request.registry.settings['model_data_dir']
    if map_dir[0] == os.path.sep:
        full_path = map_dir
    else:
        here = request.registry.settings['here']
        full_path = os.path.join(here, map_dir)
    return full_path
