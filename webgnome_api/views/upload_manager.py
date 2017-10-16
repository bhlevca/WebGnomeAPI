"""
Views for the model load/save operations.
"""
import os
import errno
import logging
import urllib

from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPUnauthorized)

from cornice import Service

from ..common.system_resources import list_files
from ..common.common_object import (get_persistent_dir)
from ..common.views import (can_persist,
                            cors_exception,
                            cors_policy,
                            cors_file_response)

log = logging.getLogger(__name__)


upload_manager = Service(name='uploads', path='/uploads*sub_folders',
                         description="Uploaded File Manager",
                         cors_policy=cors_policy)


@upload_manager.get()
@can_persist
def get_uploaded_files(request):
    '''
        Returns a listing of the persistently uploaded files.
    '''
    sub_folders = [urllib.unquote(d).encode('utf8')
                   for d in request.matchdict['sub_folders']
                   if d != '..']

    requested_path = os.path.join(get_persistent_dir(request), *sub_folders)

    try:
        return list_files(requested_path)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            # the path was found, but it is not a directory.  Try to return
            # a file response
            return cors_file_response(request, requested_path)
        elif e.errno == errno.ENOENT:
            raise cors_exception(request, HTTPNotFound)
        elif e.errno in (errno.EPERM, errno.EACCES):
            raise cors_exception(request, HTTPUnauthorized)
        else:
            raise






