"""
Views for the Spill objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

spill = Service(name='spill', path='/spill*obj_id',
                description="Spill API", cors_policy=cors_policy)

implemented_types = ('gnome.spill.spill.Spill',
                     )


@spill.get()
def get_spill(request):
    '''Returns a Gnome Spill object in JSON.'''
    return get_object(request, implemented_types)


@spill.post()
def create_spill(request):
    '''Creates a Gnome Spill object.'''
    return create_object(request, implemented_types)


@spill.put()
def update_spill(request):
    '''Updates a Gnome Spill object.'''
    return update_object(request, implemented_types)
