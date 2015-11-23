"""
Views for the model load/save operations.
"""
import os
import logging
import tempfile

from pyramid.view import view_config
from pyramid.response import Response, FileIter
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPInsufficientStorage,
                                    HTTPNotFound)

from gnome.persist import load, is_savezip_valid
from webgnome_api.common.common_object import RegisterObject
from webgnome_api.common.session_management import (init_session_objects,
                                                    set_active_model,
                                                    get_active_model)
from webgnome_api.common.views import (cors_response, 
                                       cors_exception,
                                       process_upload)

log = logging.getLogger(__name__)


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
    file_path = process_upload(request, 'new_model')
    # Now that we have our file, we will now try to load the model into
    # memory.
    # Now that we have our file, is it a zipfile?
    if not is_savezip_valid(file_path):
        raise cors_response(request, HTTPBadRequest('Incoming file is not a '
                                                    'valid zipfile!'))

    # now we try to load our model from the zipfile.
    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    log.info('semaphore acquired.')
    try:
        log.info('loading our model from zip...')
        new_model = load(file_path)
        new_model._cache.enabled = False

        init_session_objects(request, force=True)

        RegisterObject(new_model, request)

        log.info('setting active model...')
        set_active_model(request, new_model.id)
    except:
        raise cors_exception(request, HTTPBadRequest, with_stacktrace=True)
    finally:
        gnome_sema.release()
        log.info('semaphore released.')

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
        base_name = os.path.basename(tf.name)
        dir_name = os.path.dirname(tf.name)

        my_model.save(saveloc=dir_name, name=base_name)
        response_filename = ('{0}.zip'.format(my_model.name))

        tf.seek(0)

        response = request.response
        response.content_type = 'application/zip'
        response.content_disposition = ('attachment; filename={0}'
                                        .format(response_filename))
        response.app_iter = FileIter(tf)
        return response
    else:
        raise cors_response(request, HTTPNotFound('No Active Model!'))
