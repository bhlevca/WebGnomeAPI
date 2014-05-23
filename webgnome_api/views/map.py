"""
Views for the Spill objects.
"""
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

    print 'data directory = ', request.registry.settings['model_data_dir']
    print 'json map request:', json_request
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
