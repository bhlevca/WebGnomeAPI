"""
Views for the Distribution objects.
"""
from .common_object import (get_object, create_or_update_object, cors_policy)

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


@distribution.put()
def create_or_update_distribution(request):
    '''Creates or Updates a Gnome Distribution object.'''
    return create_or_update_object(request, implemented_types)
