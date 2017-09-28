"""
Views for the model load/save operations.
"""
import os
import logging
import tempfile
from threading import current_thread

from pyramid.settings import asbool
from pyramid.view import view_config
from pyramid.response import Response, FileIter
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPNotImplemented)

from cornice import Service

from gnome.persist import load, is_savezip_valid

from ..common.system_resources import list_files
from ..common.common_object import (RegisterObject,
                                    clean_session_dir,
                                    get_persistent_dir)
from ..common.session_management import (init_session_objects,
                                         set_active_model,
                                         get_active_model,
                                         acquire_session_lock)
from ..common.views import (cors_response,
                            cors_exception,
                            cors_policy,
                            process_upload)

log = logging.getLogger(__name__)


persisted_files_api = Service(name='uploaded', path='/uploaded',
                              description="Persistent Uploaded Files API",
                              cors_policy=cors_policy)


@view_config(route_name='upload', request_method='OPTIONS')
def upload_model_options(request):
    return cors_response(request, request.response)


@view_config(route_name='upload', request_method='POST')
def upload_model(request):
    '''
        Uploads a new model in the form of a zipfile and registers it as the
        current active model.

        We are generating our own filename instead of trusting
        the incoming filename since that might result in insecure paths.

        We may want to eventually use something other than /tmp,
        and if you write to an untrusted location you will need to do
        some extra work to prevent symlink attacks.
    '''
    clean_session_dir(request)
    file_path, _name = process_upload(request, 'new_model')
    # Now that we have our file, we will now try to load the model into
    # memory.
    # Now that we have our file, is it a zipfile?
    if not is_savezip_valid(file_path):
        raise cors_response(request, HTTPBadRequest('Incoming file is not a '
                                                    'valid zipfile!'))

    # now we try to load our model from the zipfile.
    session_lock = acquire_session_lock(request)
    log.info('  session lock acquired (sess:{}, thr_id: {})'
             .format(id(session_lock), current_thread().ident))
    try:
        log.info('loading our model from zip...')
        new_model = load(file_path)
        new_model._cache.enabled = False

        init_session_objects(request, force=True)

        from ..views import implemented_types

        RegisterObject(new_model, request, implemented_types)

        log.info('setting active model...')
        set_active_model(request, new_model.id)
    except Exception:
        raise cors_exception(request, HTTPBadRequest, with_stacktrace=True)
    finally:
        session_lock.release()
        log.info('  session lock released (sess:{}, thr_id: {})'
                 .format(id(session_lock), current_thread().ident))

    # We will want to clean up our tempfile when we are done.
    os.remove(file_path)

    return cors_response(request, Response('OK'))


@view_config(route_name='download')
def download_model(request):
    '''
        Here is where we save the active model as a zipfile and
        download it to the client
    '''
    my_model = get_active_model(request)

    if my_model:
        tf = tempfile.NamedTemporaryFile()
        dir_name, base_name = os.path.split(tf.name)
        tf.close()

        my_model.save(saveloc=dir_name, name=base_name)
        response_filename = ('{0}.zip'.format(my_model.name))
        tf = open(tf.name, 'r+b')
        response = request.response
        response.content_type = 'application/zip'
        response.content_disposition = ('attachment; filename={0}'
                                        .format(response_filename))
        response.app_iter = FileIter(tf)
        return response
    else:
        raise cors_response(request, HTTPNotFound('No Active Model!'))


@persisted_files_api.get()
def get_uploaded_files(request):
    '''
        Returns a listing of the persistently uploaded files.

        If the web server is not configured to persist uploaded files,
        then we raise a HTTPNotImplemented exception
    '''
    if asbool(request.registry.settings['can_persist_uploads']):
        return list_files(get_persistent_dir(request))
    else:
        raise cors_exception(request, HTTPNotImplemented)
