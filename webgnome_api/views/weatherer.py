"""
Views for the Weatherer objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

weatherer = Service(name='weatherer', path='/weatherer*obj_id',
                    description="Weatherer API", cors_policy=cors_policy)

implemented_types = ('gnome.weatherers.core.Weatherer',
                     'gnome.weatherers.Evaporation',
                     'gnome.weatherers.Emulsification',
                     'gnome.weatherers.Burn',
                     'gnome.weatherers.Skimmer',
                     'gnome.weatherers.NaturalDispersion',
                     'gnome.weatherers.Beaching',
                     'gnome.weatherers.ChemicalDispersion'
                     )


@weatherer.get()
def get_weatherer(request):
    '''Returns a Gnome Weatherer object in JSON.'''
    return get_object(request, implemented_types)


@weatherer.post()
def create_weatherer(request):
    '''Creates a Weatherer object.'''
    return create_object(request, implemented_types)


@weatherer.put()
def update_weatherer(request):
    '''Updates a Weatherer object.'''
    return update_object(request, implemented_types)
