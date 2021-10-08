"""
Views for the GOODS interface.
"""

from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPBadRequest,
                                    HTTPUnauthorized,
                                    HTTPInsufficientStorage,
                                    HTTPInternalServerError)
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_exception,
                                       cors_response,
                                       get_object,
                                       create_object,
                                       cors_policy,
                                       process_upload,
                                       can_persist,
                                       switch_to_existing_session,
                                       activate_uploaded)
from ..common.system_resources import (list_files,
                                       file_info,
                                       mkdir,
                                       rename_or_move,
                                       remove_file_or_dir,
                                       get_free_space,
                                       get_size_of_open_file,
                                       write_bufread_to_file)
from ..common.common_object import (get_session_dir,
                                    get_persistent_dir)
from ..common.views import (can_persist,
                            get_size_of_open_file,
                            gen_unique_filename,
                            cors_exception,
                            cors_policy,
                            cors_response,
                            cors_file_response)

import ujson
import os
import urllib.request

from pyramid.response import Response
from pyramid.view import view_config

from cornice import Service


import logging
log = logging.getLogger(__name__)

goods = Service(name='goods', path='/goods*',
                       description="GOODS API", cors_policy=cors_policy)


@goods.post()
def get_goods_map(request):
    '''
    Uses the payload passed by the client to make a .bna download request from GOODS.
    This file is then used to create a map object, which is then returned to the client
    '''
    goods_resp = urllib.request.urlopen('https://gnome.orr.noaa.gov/goods/tools/GSHHS/coast_extract', request.body)
    fn = goods_resp.headers.get_filename()
    size = goods_resp.length
    max_upload_size = eval(request.registry.settings['max_upload_size'])

    if size > max_upload_size:
        raise cors_response(request,
                            HTTPBadRequest('file is too big!  Max size = {}'
                                           .format(max_upload_size)))

    upload_dir = os.path.relpath(get_session_dir(request))
    if size >= get_free_space(upload_dir):
        raise cors_response(request,
                            HTTPInsufficientStorage('Not enough space '
                                                    'to save the file'))


    file_name, unique_name = gen_unique_filename(fn, upload_dir)

    file_path = os.path.join(upload_dir, unique_name)

    write_bufread_to_file(goods_resp.fp, file_path)

    goods_resp.close()

    log.info('Successfully uploaded file "{0}"'.format(file_path))

    return file_path, file_name
