"""
Views for the Environment objects.
This currently includes Wind and Tide objects.
"""
import ujson
import os

from pyramid.response import Response
from pyramid.view import view_config

from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy,
                                       cors_response,
                                       cors_exception,
                                       process_upload)

from cornice import Service

env = Service(name='environment', path='/environment*obj_id',
              description="Environment API",
              cors_policy=cors_policy)

implemented_types = ('gnome.environment.Tide',
                     'gnome.environment.Wind',
                     'gnome.environment.Water',
                     'gnome.environment.Waves',
                     'gnome.environment.environment_objects.GridCurrent',
                     'gnome.environment.grid_property.GriddedProp',
                     'gnome.environment.grid_property.GridVectorProp',
                     'gnome.environment.ts_property.TimeSeriesProp',
                     )


@env.get()
def get_environment(request):
    '''Returns an Gnome Environment object in JSON.'''
    return get_object(request, implemented_types)


@env.post()
def create_environment(request):
    '''Creates an Environment object.'''
    return create_object(request, implemented_types)


@env.put()
def update_environment(request):
    '''Updates an Environment object.'''
    return update_object(request, implemented_types)


@view_config(route_name='environment_upload', request_method='OPTIONS')
def environment_upload_options(request):
    return cors_response(request, request.response)


@view_config(route_name='environment_upload', request_method='POST')
def environment_upload(request):
    filename, name = process_upload(request, 'new_environment')
    resp = Response(ujson.dumps({'filename': filename, 'name': name}))

    return cors_response(request, resp)
