"""
Views for the Outputter objects.
"""
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

outputter = Service(name='outputter', path='/outputter*obj_id',
                  description="Outputter API", cors_policy=cors_policy)

implemented_types = ('gnome.outputters.outputter.Outputter',
                     'gnome.outputters.renderer.Renderer',
                     'gnome.outputters.netcdf.NetCDFOutput',
                     'gnome.outputters.geo_json.GeoJson')


@outputter.get()
def get_outputter(request):
    '''Returns a Gnome Outputter object in JSON.'''
    return get_object(request, implemented_types)


@outputter.post()
def create_outputter(request):
    '''Creates a Gnome Outputter object.'''
    return create_object(request, implemented_types)


@outputter.put()
def update_outputter(request):
    '''Updates a Gnome Outputter object.'''
    return update_object(request, implemented_types)
