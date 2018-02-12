"""
Views for file download operations.
"""
from os import walk
from os.path import isfile, isdir, basename, join, sep
import zipfile

from uuid import uuid4

from pyramid.view import view_config
from pyramid.response import FileResponse
from pyramid.httpexceptions import HTTPNotFound

from webgnome_api.common.common_object import get_session_dir
from webgnome_api.common.session_management import get_active_model
from webgnome_api.common.views import cors_response


@view_config(route_name='export', request_method='GET')
def download_file(request):
    obj_id = uuid4()
    session_path = get_session_dir(request)
    file_path = sep.join(map(str, request.matchdict['file_path']))
    output_path = join(session_path, file_path)

    try:
        model_name = get_active_model(request).name
    except Exception:
        raise cors_response(request, HTTPNotFound('No Active Model!'))

    if isdir(output_path):
        output_zip_path = "{0}_{1}_output.zip".format(model_name, obj_id)
        zip_path = join(output_path, output_zip_path)
        zf = zipfile.ZipFile(zip_path, "w")

        for dirname, _subdirs, files in walk(output_path):
            for filename in files:
                if (not filename.endswith(output_zip_path) and
                        not isdir(filename)):
                    zipfile_path = join(dirname, filename)
                    zf.write(zipfile_path, basename(zipfile_path))

        zf.close()

        response = FileResponse(zip_path, request)
        response.headers['Content-Disposition'] = ("attachment; filename={0}"
                                                   .format(basename(zip_path)))
        return response
    elif isfile(output_path):
        return FileResponse(output_path, request)
    else:
        raise cors_response(request, HTTPNotFound('File(s) requested do not '
                                                  'exist on the server!'))
