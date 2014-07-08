"""
Views for the Initializer objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

initializer = Service(name='initializer', path='/initializer*obj_id',
                      description="Iinitializer API", cors_policy=cors_policy)

implemented_types = ('gnome.spill.elements.InitWindages',
                     'gnome.spill.elements.InitMassComponentsFromOilProps',
                     'gnome.spill.elements.InitHalfLivesFromOilProps',
                     'gnome.spill.elements.InitMassFromTotalMass',
                     'gnome.spill.elements.InitMassFromPlume',
                     'gnome.spill.elements.InitRiseVelFromDist',
                     'gnome.spill.elements.InitRiseVelFromDropletSizeFromDist',
                     'gnome.spill.elements.InitHalfLivesFromOilProps',
                     )


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
