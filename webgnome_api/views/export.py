"""
Views for file download operations.
"""
import os
import logging
import zipfile

from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPInsufficientStorage,
                                    HTTPNotFound)

from gnome.persist import load, is_savezip_valid
from webgnome_api.common.common_object import get_session_dir
from webgnome_api.common.session_management import (init_session_objects,
                                                    set_active_model,
                                                    get_active_model,
                                                    acquire_session_lock)
from webgnome_api.common.views import (cors_response,
                                       cors_exception,
                                       process_upload)


@view_config(route_name='export', request_method='GET')
def download_file(request):
    session_path = get_session_dir(request)
    file_path = os.path.sep.join(map(str, request.matchdict['file_path']))
    output_path = os.path.join(session_path, file_path)

    try:
        model_name = get_active_model(request).name
    except:
        raise cors_response(request, HTTPNotFound('No Active Model!'))

    if os.path.isdir(output_path):
        zip_path = os.path.join(output_path, "{0}_output.zip".format(model_name))
        zf = zipfile.ZipFile(zip_path, "w")
        for dirname, subdirs, files in os.walk(output_path):
            for filename in files:
                if not filename.endswith('_output.zip') and not os.path.isdir(filename):
                    zipfile_path = os.path.join(dirname, filename)
                    zf.write(zipfile_path, os.path.basename(zipfile_path))
        zf.close()
        return FileResponse(zip_path, request)
    elif os.path.isfile(output_path):
        return FileResponse(output_path, request)
    else:
        raise cors_response(request, HTTPNotFound('File(s) requested do not exist on the server!'))
