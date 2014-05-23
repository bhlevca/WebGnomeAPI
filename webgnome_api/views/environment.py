"""
Views for the Environment objects.
This currently includes Wind and Tide objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

env = Service(name='environment', path='/environment*obj_id',
              description="Environment API",
              cors_policy=cors_policy)

implemented_types = ('gnome.environment.Tide',
                     'gnome.environment.Wind',
                     )


@env.get()
def get_environment(request):
    '''Returns an Gnome Environment object in JSON.'''
    return get_object(request, implemented_types)


@env.post()
def create_environment(request):
    '''Creates an Environment object.'''
    return create_object(request, implemented_types)


@env.put()
def update_environment(request):
    '''Updates an Environment object.'''
    return update_object(request, implemented_types)
