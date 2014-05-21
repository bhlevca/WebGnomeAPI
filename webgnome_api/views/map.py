"""
Views for the Spill objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

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
    return create_object(request, implemented_types)


@map_api.put()
def update_map(request):
    '''Updates a Gnome Map object.'''
    return update_object(request, implemented_types)
