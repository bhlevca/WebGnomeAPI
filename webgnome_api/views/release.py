"""
Views for the Release objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

release = Service(name='release', path='/release*obj_id',
                  description="Release API", cors_policy=cors_policy)

implemented_types = ('gnome.spill.release.PointLineRelease',
                     'gnome.spill.release.SpatialRelease',
                     'gnome.spill.release.VerticalPlumeRelease',
                     )


@release.get()
def get_release(request):
    '''Returns a Gnome Release object in JSON.'''
    return get_object(request, implemented_types)


@release.post()
def create_release(request):
    '''Creates a Gnome Release object.'''
    return create_object(request, implemented_types)


@release.put()
def update_release(request):
    '''Updates a Gnome Release object.'''
    return update_object(request, implemented_types)
