"""
Views for the model load/save operations.
"""
import os
import uuid
import shutil
import logging
import tempfile

from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPInsufficientStorage,
                                    HTTPNotFound)

from gnome.persist import load, is_savezip_valid
from webgnome_api.common.common_object import RegisterObject
from webgnome_api.common.session_management import (init_session_objects,
                                                    set_active_model,
                                                    get_active_model)

log = logging.getLogger(__name__)


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
    # ``input_file`` contains the actual file data which needs to be
    # stored somewhere.
    base_dir = os.path.join(request.registry.settings['here'],
                            request.registry.settings['save_file_dir'])
    max_upload_size = eval(request.registry.settings['max_upload_size'])
    log.info('save_file_dir: {0}'.format(base_dir))
    log.info('max_upload_size: {0}'.format(max_upload_size))

    input_file = request.POST['new_model'].file

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
        raise HTTPBadRequest('file is too big!  Max size = {0}'
                             .format(max_upload_size))

    # now we check if we have enough space to save the file.
    free_bytes = os.statvfs(base_dir).f_bfree
    if size >= free_bytes:
        raise HTTPInsufficientStorage('Not enough space to save the file')

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
        raise HTTPBadRequest('Incoming file is not a valid zipfile!')

    # now we try to load our model from the zipfile.
    try:
        new_model = load(file_path)
        new_model._cache.enabled = False
    except:
        raise HTTPBadRequest('Failed to load model from Incoming file!')

    # Now we try to register our new model.
    init_session_objects(request, force=True)
    RegisterObject(new_model, request)
    set_active_model(request, new_model.id)

    # We will want to clean up our tempfile when we are done.
    os.remove(file_path)

    return Response('OK')


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

        return FileResponse(tf.name,
                            request=request,
                            content_type='application/octet-stream')
    else:
        raise HTTPNotFound('No Active Model!')
