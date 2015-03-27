"""
Views for the model load/save operations.
"""
import os
import uuid
import shutil
import logging

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest, HTTPInsufficientStorage

log = logging.getLogger(__name__)


@view_config(route_name='load', request_method='POST')
def load_model(request):
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

    # We first write to a temporary file to prevent incomplete files from
    # being used.
    file_name = '{0}.zip'.format(uuid.uuid4())
    file_path = os.path.join(base_dir, file_name)

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
    input_file.seek(0)
    with open(file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    # Now that we have our file, we will now try to load the model into
    # memory.
    log.info('\tSuccessfully uploaded file "{0}"'.format(file_path))
    log.info('\tNot doing anything with it yet, though.')

    # We will want to clean up our tempfile when we are done.
    # os.remove(file_path)

    return Response('OK')
