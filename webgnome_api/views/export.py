"""
Views for file download operations.
"""
import os
import logging
import tempfile
from threading import current_thread

from pyramid.view import view_config
from pyramid.response import Response, FileIter
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPInsufficientStorage,
                                    HTTPNotFound)

from gnome.persist import load, is_savezip_valid
from webgnome_api.common.common_object import RegisterObject, clean_session_dir
from webgnome_api.common.session_management import (init_session_objects,
                                                    set_active_model,
                                                    get_active_model,
                                                    acquire_session_lock)
from webgnome_api.common.views import (cors_response,
                                       cors_exception,
                                       process_upload)
