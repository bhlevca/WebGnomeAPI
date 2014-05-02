"""
Views for the ElementType objects.
"""
from .common_object import (get_object, create_or_update_object, cors_policy)

from cornice import Service

element_type = Service(name='element_type', path='/element_type*obj_id',
                      description="ElementType API", cors_policy=cors_policy)

implemented_types = ('gnome.spill.elements.ElementType',
                     )


@element_type.get()
def get_element_type(request):
    '''Returns a Gnome ElementType object in JSON.'''
    return get_object(request, implemented_types)


@element_type.put()
def create_or_update_element_type(request):
    '''Creates or Updates a Gnome ElementType object.'''
    return create_or_update_object(request, implemented_types)
