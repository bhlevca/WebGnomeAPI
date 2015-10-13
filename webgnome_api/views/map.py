"""
Views for the Map objects.
"""
import os
import ujson
import logging

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
                                               obj_id_from_req_payload,
                                               get_file_path)

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

log = logging.getLogger(__name__)


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
    log_prefix = 'req({0}): create_map():'.format(id(request))
    init_session_objects(request)

    try:
        json_request = ujson.loads(request.body)
    except:
        raise cors_exception(request, HTTPBadRequest)

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise cors_exception(request, HTTPNotImplemented)

    if 'filename' in json_request:
        json_request['filename'] = get_file_path(request, json_request=json_request)

    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    log.info('  ' + log_prefix + 'semaphore acquired...')

    try:
        obj = CreateObject(json_request, get_session_objects(request))
    except:
        raise cors_exception(request, HTTPUnsupportedMediaType,
                             with_stacktrace=True)
    finally:
        gnome_sema.release()
        log.info('  ' + log_prefix + 'semaphore released...')

    set_session_object(obj, request)
    return obj.serialize()


@map_api.put()
def update_map(request):
    '''Updates a Gnome Map object.'''
    try:
        json_request = ujson.loads(request.body)
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
                    if primary_id not in ('SpillableArea', 'Map Bounds'):
                        geom_json = f.GetGeometryRef().ExportToJson()
                        geom_json = geom_json[42:-4]
                        shoreline_geo += geom_json + ', '

            # remove last comma from geometry
            shoreline_geo = shoreline_geo[0:-2]

            # TODO: Why are we forming a string instead of a MultiPolygon obj?
            #       Answer: because we are using a homebrew FeatureCollection
            #               object.
            json_body = ('{{'
                         '  "properties": {{'
                         '    "name": "Shoreline"'
                         '  }},'
                         '  "geometry": {{'
                         '    "type": "MultiPolygon",'
                         '    "coordinates": [ {0}'
                         '    ]'
                         '  }}'
                         '}}'
                         .format(shoreline_geo))
            shoreline_feature = ujson.loads(json_body)

            return FeatureCollection([shoreline_feature]).serialize()
        else:
            raise cors_exception(request, HTTPNotImplemented)
    else:
        raise cors_exception(request, HTTPNotFound)
