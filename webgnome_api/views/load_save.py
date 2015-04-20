"""
Views for the model load/save operations.
"""
import os
import uuid
import shutil
import logging
import tempfile

from pyramid.view import view_config
from pyramid.response import Response, FileIter
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPInsufficientStorage,
                                    HTTPNotFound)
from pyramid_redis_sessions.session import RedisSession

from gnome.persist import load, is_savezip_valid
from webgnome_api.common.common_object import RegisterObject
from webgnome_api.common.session_management import (init_session_objects,
                                                    set_active_model,
                                                    get_active_model)
from webgnome_api.common.views import cors_response, cors_exception

log = logging.getLogger(__name__)


@view_config(route_name='upload', request_method='OPTIONS')
def upload_model_options(request):
    req_origin = request.headers.get('Origin')
    if req_origin is not None:
        request.response.headers.add('Access-Control-Allow-Origin', req_origin)
        request.response.headers.add('Access-Control-Allow-Credentials',
                                     'true')
        req_headers = request.headers.get('Access-Control-Request-Headers')
        request.response.headers.add('Access-Control-Allow-Headers',
                                     req_headers)

    return request.response


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
    base_dir = request.registry.settings['save_file_dir']
    max_upload_size = eval(request.registry.settings['max_upload_size'])

    log.info('save_file_dir: {0}'.format(base_dir))
    log.info('max_upload_size: {0}'.format(max_upload_size))

    input_file = request.POST['new_model'].file

    # For some reason, the multipart form does not contain
    # a session cookie, and Nathan so far has not been able to explicitly
    # set it.  So a workaround is to put the session ID in the form as
    # hidden POST content.
    # Note: This could break in the future if the RedisSession API changes.
    redis_session_id = request.POST['session']
    if redis_session_id in request.session.redis.keys():
        redis_session = RedisSession(request.session.redis,
                                     redis_session_id,
                                     request.session.timeout,
                                     request.session.delete_cookie)
        request.session = redis_session

    # select a unique filename and a folder to put it in
    # folder name will be the same unique name as the file
    folder_name = '{0}'.format(uuid.uuid4())
    file_name = '{0}.zip'.format(folder_name)
    folder_path = os.path.join(base_dir, folder_name)
    file_path = os.path.join(folder_path, file_name)

    # check the size of our incoming file
    input_file.seek(0, 2)
    size = input_file.tell()
    log.info('Incoming file size: {0}'.format(size))

    if size > max_upload_size:
        raise cors_response(request,
                            HTTPBadRequest('file is too big!  Max size = {0}'
                                           .format(max_upload_size)))

    # now we check if we have enough space to save the file.
    free_bytes = os.statvfs(base_dir).f_bfree
    if size >= free_bytes:
        raise cors_response(request,
                            HTTPInsufficientStorage('Not enough space '
                                                    'to save the file'))

    # Finally write the data to a temporary file
    os.mkdir(folder_path)
    input_file.seek(0)
    with open(file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    # Now that we have our file, we will now try to load the model into
    # memory.
    log.info('\tSuccessfully uploaded file "{0}"'.format(file_path))

    # Now that we have our file, is it a zipfile?
    if not is_savezip_valid(file_path):
        raise cors_response(request,
                            HTTPBadRequest('Incoming file is not a '
                                           'valid zipfile!'))

    # now we try to load our model from the zipfile.
    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()
    log.info('semaphore acquired.')
    try:
        log.info('loading our model from zip...')
        new_model = load(file_path)
        new_model._cache.enabled = False

        # Now we try to register our new model.
        init_session_objects(request, force=True)
        RegisterObject(new_model, request)

        log.info('setting active model...')
        set_active_model(request, new_model.id)
    except:
        raise cors_exception(request, HTTPBadRequest)
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
