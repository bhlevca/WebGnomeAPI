"""
Views for the Substance objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

substance = Service(name='substance', path='/substance*obj_id',
                       description="Substance API", cors_policy=cors_policy)

implemented_types = ('gnome.spill.substance.GnomeOil',
                     'gnome.spill.substance.NonWeatheringSubstance'
                     )


@substance.get()
def get_substance(request):
    '''Returns a Gnome Substance object in JSON.'''
    return get_object(request, implemented_types)


@substance.post()
def create_substance(request):
    '''Creates a Gnome Substance object.'''
    return create_object(request, implemented_types)


@substance.put()
def update_substance(request):
    '''Updates a Gnome Substance object.'''
    return update_object(request, implemented_types)
