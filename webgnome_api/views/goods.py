"""
Views for the GOODS interface.
"""

from pyramid.httpexceptions import (HTTPRequestTimeout,
                                    HTTPInsufficientStorage,
                                    HTTPBadRequest)

from ..common.system_resources import (get_free_space,
                                       write_bufread_to_file)

from ..common.common_object import (get_session_dir)

from ..common.views import (switch_to_existing_session,
                            gen_unique_filename,
                            cors_exception,
                            cors_policy,
                            cors_response)

from libgoods import maps, api

import os
import shutil
import urllib.request
import socket
import ujson
from cornice import Service

import logging

log = logging.getLogger(__name__)

goods_maps = Service(name='maps', path='/goods/maps*',
                description="GOODS MAP API", cors_policy=cors_policy)

goods_currents = Service(name='currents', path='/goods/currents*',
                      description="GOODS CURRENTS API", cors_policy=cors_policy)

goods_list_models = Service(name='list_models', path='/goods/list_models',
                            description="GOODS METADATA API", cors_policy=cors_policy)


@goods_list_models.get()
def get_model_metadata(request):
    '''
    gets set of metadata for all available models
    '''
    
    bounds = ujson.loads(request.GET['map_bounds'])
    metadata = api.filter_models(bounds)

    return metadata


@goods_maps.post()
def get_goods_map(request):
    '''
    Uses the payload passed by the client to make a .bna download request from GOODS.
    This file is then used to create a map object, which is then returned to the client
    '''
    # Example post:
    # req_params = {'err_placeholder':'',
    #               'NorthLat': 47.06693175688763,
    #               'WestLon': -124.26942110656861,
    #               'EastLon': -123.6972360021842,
    #               'SouthLat': 46.78488364986247,
    #               'xDateline': 0,
    #               'resolution': 'i',
    #               'submit': 'Get Map',
    #               }

    params = request.POST

    # In the future, the webgnome API should be a closer match
    # to the libgoods api.
    max_upload_size = eval(request.registry.settings['max_upload_size'])
    bounds = ((float(params['WestLon']), float(params['SouthLat'])),
              (float(params['EastLon']), float(params['NorthLat'])))

    try:
        fn, contents = maps.get_map(
            bounds=bounds,
            resolution=params['resolution'],
            shoreline=params['shoreline'],
            cross_dateline=bool(int(params['xDateline'])),
            max_filesize=max_upload_size,
        )

    except maps.FileTooBigError:
        raise cors_response(request,
                            HTTPBadRequest('file is too big!  Max size = {}'
                                           .format(max_upload_size)))

    size = len(contents)

    upload_dir = os.path.relpath(get_session_dir(request))

    if size >= get_free_space(upload_dir):
        raise cors_response(request,
                            HTTPInsufficientStorage('Not enough space '
                                                    'to save the file'))

    file_name, unique_name = gen_unique_filename(fn, upload_dir)

    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, 'w') as fp:
        fp.write(contents)

    log.info('Successfully uploaded file "{0}"'.format(file_path))

    return file_path, file_name

@goods_currents.get()
def get_currents_data(request):
    #stub function multi-endpoint GET request (similar to grid)
    params = request.GET
    option = params['option']
    if option == 'bounding_poly':
        return 

@goods_currents.post()
def get_currents(request):
    '''
    Uses the payload passed by the client to send information to
    libGOODS. This file returned from libgoods is then used to create a
    PyCurrentMover object, which is then returned to the client
    '''

    upload_dir = os.path.relpath(get_session_dir(request))
    params = request.POST
    max_upload_size = eval(request.registry.settings['max_upload_size'])
    bounds = ((float(params['WestLon']), float(params['SouthLat'])),
              (float(params['EastLon']), float(params['NorthLat'])))
    try:
        fp = api.get_model_data(
            model_id=params['model_name'].upper(),
            bounds=bounds,
            time_interval=(None, None),
            environmental_parameters=['surface currents'],
            cross_dateline=bool(int(params['xDateline'])),
            max_filesize=max_upload_size,
        )

        file_name, unique_name = gen_unique_filename(fp.name, upload_dir)

        file_path = os.path.join(upload_dir, unique_name)
        shutil.move(fp, file_path)  # maybe I should pass session directory location to libgoods?

        log.info('Successfully uploaded file "{0}"'.format(file_path))

    except api.FileTooBigError:
            raise cors_response(request,
                                HTTPBadRequest('file is too big! '
                                               f'Max size = {max_upload_size}'))

    return file_path

