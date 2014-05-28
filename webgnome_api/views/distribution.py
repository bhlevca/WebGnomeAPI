"""
Views for the Distribution objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

distribution = Service(name='distribution', path='/distribution*obj_id',
                      description="Distribution API", cors_policy=cors_policy)

implemented_types = ('gnome.utilities.distributions.UniformDistribution',
                     'gnome.utilities.distributions.NormalDistribution',
                     'gnome.utilities.distributions.LogNormalDistribution',
                     'gnome.utilities.distributions.WeibullDistribution')


@distribution.get()
def get_distribution(request):
    '''Returns a Gnome Distribution object in JSON.'''
    return get_object(request, implemented_types)


@distribution.post()
def create_distribution(request):
    '''Creates a Gnome Distribution object.'''
    return create_object(request, implemented_types)


@distribution.put()
def update_distribution(request):
    '''Updates a Gnome Distribution object.'''
    return update_object(request, implemented_types)
