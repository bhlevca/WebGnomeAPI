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
from libgoods import map, currents

import os
import shutil
import urllib.request
import socket
from cornice import Service

import logging

log = logging.getLogger(__name__)

goods = Service(name='goods', path='/goods*',
                description="GOODS API", cors_policy=cors_policy)

goods_hycom = Service(name='goods_hycom', path='/goods_hycom*',
                      description="GOODS API", cors_policy=cors_policy)


@goods.post()
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

    # goods_resp = urllib.request.urlopen('https://gnome.orr.noaa.gov/goods/tools/GSHHS/coast_extract', request.body)

    params = request.POST

    # In the future, the webgnome API should be a closer match
    # to the libgoods api.
    max_upload_size = eval(request.registry.settings['max_upload_size'])
    try:
        fn, contents = map.get_map(north_lat=float(params['NorthLat']),
                                        south_lat=float(params['SouthLat']),
                                        west_lon=float(params['WestLon']),
                                        east_lon=float(params['EastLon']),
                                        resolution=params['resolution'],
                                        cross_dateline=bool(int(params['xDateline'])),
                                        max_filesize=max_upload_size,
                                        )

    except map.FileTooBigError:
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

@goods_hycom.post()
def get_currrents(request):
    '''
    Uses the payload passed by the client to send information to libGOODS.
    This file returned from libgoods is then used to create a PyCurrentMover object, which is then returned
    to the client
    ''' 
    
    switch_to_existing_session(request)
    upload_dir = os.path.relpath(get_session_dir(request))
    params = request.POST
    fn, fp = currents.get_currents(model_name=params['model_name'],
                            north_lat=float(params['NorthLat']),
                            south_lat=float(params['SouthLat']),
                            west_lon=float(params['WestLon']),
                            east_lon=float(params['EastLon']),
                            cross_dateline=bool(int(params['xDateline'])),
                            )
                            
    file_name, unique_name = gen_unique_filename(fn, upload_dir)
    
    file_path = os.path.join(upload_dir, unique_name)
    shutil.move(fp, file_path) # maybe I should pass session directory location to libgoods?
        
    log.info('Successfully uploaded file "{0}"'.format(file_path))

    return file_path

