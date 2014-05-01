"""
Views for the Spill objects.
"""
from .common_object import (get_object, create_or_update_object, cors_policy)

from cornice import Service

spill = Service(name='spill', path='/spill*obj_id',
                description="Spill API", cors_policy=cors_policy)

implemented_types = ('gnome.spill.spill.Spill',
                     )


@spill.get()
def get_spill(request):
    '''Returns a Gnome Spill object in JSON.'''
    return get_object(request, implemented_types)


@spill.put()
def create_or_update_spill(request):
    '''Creates or Updates a Gnome Spill object.'''
    return create_or_update_object(request, implemented_types)
