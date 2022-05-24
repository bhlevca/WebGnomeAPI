"""
Views for the Map objects.
"""
import os
import logging
from threading import current_thread
import zlib

import ujson
import numpy as np

from cornice import Service

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType,
                                    HTTPNotImplemented)

from webgnome_api.common.views import (can_persist,
                                       cors_exception,
                                       cors_response,
                                       get_object,
                                       create_object,
                                       cors_policy,
                                       activate_uploaded,
                                       web_ser_opts)

from webgnome_api.common.common_object import (UpdateObject,
                                               ObjectImplementsOneOf,
                                               obj_id_from_url,
                                               obj_id_from_req_payload)

from webgnome_api.common.session_management import (get_session_objects,
                                                    get_session_object,
                                                    set_session_object,
                                                    acquire_session_lock)

from webgnome_api.common.helpers import JSONImplementsOneOf

map_api = Service(name='map', path='/map*obj_id',
                  description="Map API", cors_policy=cors_policy)

implemented_types = ('gnome.maps.map.GnomeMap',
                     'gnome.maps.map.MapFromBNA',
                     'gnome.maps.map.ParamMap',
                     )

log = logging.getLogger(__name__)


@map_api.get()
def get_map(request):
    '''Returns a Gnome Map object in JSON.'''
    content_requested = request.matchdict.get('obj_id')
    resp = Response(
        content_type='arraybuffer',
        content_encoding='deflate'
    )
    route = content_requested[1] if len(content_requested) > 1 else None
    if (len(content_requested) > 1):
        if route == 'raster':
            resp.body, shape, bbox = get_raster(request)
            resp.headers.add('Access-Control-Expose-Headers', 'shape')
            resp.headers.add('Access-Control-Expose-Headers', 'bbox')
            resp.headers.add('shape', str(shape))
            resp.headers.add('bbox', str(bbox))
            return cors_response(request, resp)

        if route == 'geojson':
            return get_geojson(request, implemented_types)
    else:
        return get_object(request, implemented_types)


@map_api.post()
def create_map_view(request):
    return create_map(request)


def create_map(request):
    return create_object(request, implemented_types)


@map_api.put()
def update_map(request):
    '''Updates a Gnome Map object.'''
    try:
        json_request = ujson.loads(request.body.decode('utf-8'))
    except Exception:
        raise cors_exception(request, HTTPBadRequest)

    if not JSONImplementsOneOf(json_request, implemented_types):
        raise cors_exception(request, HTTPNotImplemented)

    obj = get_session_object(obj_id_from_req_payload(json_request),
                             request)
    if obj:
        try:
            UpdateObject(obj, json_request, get_session_objects(request))
        except Exception:
            raise cors_exception(request, HTTPUnsupportedMediaType,
                                 with_stacktrace=True)
    else:
        raise cors_exception(request, HTTPNotFound)

    set_session_object(obj, request)
    return obj.serialize(options=web_ser_opts)


@view_config(route_name='map_upload', request_method='OPTIONS')
def upload_map_options(request):
    return cors_response(request, request.response)


@view_config(route_name='map_upload', request_method='POST')
def upload_map(request):
    log_prefix = 'req({0}): upload_map():'.format(id(request))
    log.info('>>{}'.format(log_prefix))

    name = request.POST['name']
    file_list = request.POST['file_list']
    file_list = ujson.loads(file_list)
    file_name = file_list[0]

    log.info('  {} file_name: {}, name: {}'
             .format(log_prefix, file_name, name))

    # fixme: why is this not just calling the pygnome code directly?
    request.body = ujson.dumps({'obj_type': 'gnome.maps.map.MapFromBNA',
                                'filename': file_name,
                                'refloat_halflife': 6.0,
                                'name': name
                                }).encode('utf-8')

    map_obj = create_map(request)
    resp = Response(ujson.dumps(map_obj))

    log.info('<<{}'.format(log_prefix))
    return cors_response(request, resp)


@view_config(route_name='map_activate', request_method='OPTIONS')
def activate_map_options(request):
    return cors_response(request, request.response)


@view_config(route_name='map_activate', request_method='POST')
@can_persist
def activate_map(request):
    '''
        Activate a map that has already been persistently uploaded.
    '''
    log_prefix = 'req({0}): activate_map():'.format(id(request))
    log.info('>>{}'.format(log_prefix))

    file_name, name = activate_uploaded(request)
    file_path = file_name.split(os.path.sep)[-1]

    request.body = ujson.dumps({'obj_type': 'gnome.maps.map.MapFromBNA',
                                'filename': file_path,
                                'refloat_halflife': 6.0,
                                'name': name
                                }).encode('utf-8')

    map_obj = create_map(request)
    resp = Response(ujson.dumps(map_obj))

    log.info('<<{}'.format(log_prefix))
    return cors_response(request, resp)


def get_geojson(request, implemented_types):
    '''Returns the GeoJson for a Gnome Map object.'''
    obj = get_session_object(obj_id_from_url(request), request)

    if obj:
        if ObjectImplementsOneOf(obj, implemented_types):
            return obj.to_geojson()
        else:
            raise cors_exception(request, HTTPNotImplemented)
    else:
        raise cors_exception(request, HTTPNotFound)


def get_raster(request):
    '''
        Outputs the map's raster in binary format
    '''
    log_prefix = 'req({0}): get_raster():'.format(id(request))
    log.info('>>' + log_prefix)

    session_lock = acquire_session_lock(request)
    log.info('  {} session lock acquired (sess:{}, thr_id: {})'
             .format(log_prefix, id(session_lock), current_thread().ident))
    try:
        obj_id = request.matchdict.get('obj_id')[0]
        obj = get_session_object(obj_id, request)

        if obj is not None:
            raster = obj.raster.copy()
            # transpose for client
            bbox = obj.land_polys.bounding_box.AsPoly().reshape(-1).tolist()

            return (zlib.compress(np.ascontiguousarray(raster.T).tobytes()),
                    raster.T.shape, bbox)
        else:
            exc = cors_exception(request, HTTPNotFound)
            raise exc
    finally:
        session_lock.release()
        log.info('  {} session lock released (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

    log.info('<<' + log_prefix)
