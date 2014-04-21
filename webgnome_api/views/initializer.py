"""
Views for the Initializer objects.
"""
from .common_object import (get_object, create_or_update_object, cors_policy)

from cornice import Service

initializer = Service(name='initializer', path='/initializer*obj_id',
                      description="Iinitializer API", cors_policy=cors_policy)

implemented_types = ('gnome.spill.elements.InitWindages',
                     'gnome.spill.elements.InitMassComponentsFromOilProps',
                     'gnome.spill.elements.InitHalfLivesFromOilProps',
                     'gnome.spill.elements.InitMassFromTotalMass',
                     'gnome.spill.elements.InitMassFromVolume',
                     'gnome.spill.elements.InitMassFromPlume',
                     'gnome.spill.elements.InitRiseVelFromDist',
                     'gnome.spill.elements.InitRiseVelFromDropletSizeFromDist',
                     'gnome.spill.elements.InitHalfLivesFromOilProps',
                     )


@initializer.get()
def get_initializer(request):
    '''Returns a Gnome Initializer object in JSON.'''
    return get_object(request, implemented_types)


@initializer.put()
def create_or_update_initializer(request):
    '''Creates or Updates a Gnome Initializer object.'''
    return create_or_update_object(request, implemented_types)
