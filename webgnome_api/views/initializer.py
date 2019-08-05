"""
Views for the Initializer objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

initializer = Service(name='initializer', path='/initializer*obj_id',
                      description="Initializer API", cors_policy=cors_policy)

module_name = 'gnome.spill.initializers'
module_attrs = ('InitWindages',
                'InitMassFromPlume',
                'InitRiseVelFromDist',
                'InitRiseVelFromDropletSizeFromDist',
                )

implemented_types = ['{0}.{1}'.format(module_name, a)
                     for a in module_attrs]


@initializer.get()
def get_initializer(request):
    '''Returns a Gnome Initializer object in JSON.'''
    return get_object(request, implemented_types)


@initializer.post()
def create_initializer(request):
    '''Creates a Gnome Initializer object.'''
    return create_object(request, implemented_types)


@initializer.put()
def update_initializer(request):
    '''Updates a Gnome Initializer object.'''
    return update_object(request, implemented_types)
