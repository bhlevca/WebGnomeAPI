"""
Views for the Appearance objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

appearance = Service(name='appearance', path='/appearance*obj_id',
                description="appearance API", cors_policy=cors_policy)

implemented_types = (
    'gnome.utilities.appearance.Colormap',
    'gnome.utilities.appearance.MapAppearance',
    'gnome.utilities.appearance.MoverAppearance',
    'gnome.utilities.appearance.GridAppearance',
    'gnome.utilities.appearance.VectorAppearance',
    'gnome.utilities.appearance.Appearance',
    'gnome.utilities.appearance.SpillAppearance'
)


@appearance.get()
def get_appearance(request):
    '''Returns a Gnome appearance object in JSON.'''
    return get_object(request, implemented_types)


@appearance.post()
def create_appearance(request):
    '''Creates a Gnome appearance object.'''
    return create_object(request, implemented_types)


@appearance.put()
def update_appearance(request):
    '''Updates a Gnome appearance object.'''
    return update_object(request, implemented_types)