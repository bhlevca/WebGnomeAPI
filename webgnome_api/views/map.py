"""
Views for the Spill objects.
"""
import os
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

map_api = Service(name='map', path='/map*obj_id',
                  description="Map API", cors_policy=cors_policy)

implemented_types = ('gnome.map.MapFromBNA',
                     )


@map_api.get()
def get_map(request):
    '''Returns a Gnome Map object in JSON.'''
    return get_object(request, implemented_types)


@map_api.post()
def create_map(request):
    '''Creates a Gnome Map object.'''
    init_session_objects(request.session)
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

    obj = CreateObject(json_request, request.session['objects'])

    set_session_object(obj, request.session)
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
                             request.session)
    if obj:
        try:
            UpdateObject(obj, json_request, request.session['objects'])
        except ValueError as e:
            raise HTTPUnsupportedMediaType(e)
    else:
        raise HTTPNotFound()

    set_session_object(obj, request.session)
    return obj.serialize()


def get_map_dir_from_config(request):
    map_dir = request.registry.settings['model_data_dir']
    if map_dir[0] == os.path.sep:
        full_path = map_dir
    else:
        here = request.registry.settings['here']
        full_path = os.path.join(here, map_dir)
    return full_path
