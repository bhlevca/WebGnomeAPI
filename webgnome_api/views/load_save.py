"""
Views for the model load/save operations.
"""
import os
import uuid
import shutil
import logging

from cornice import Service
from pyramid.response import Response

from webgnome_api.common.views import cors_exception, cors_policy

load_api = Service(name='load_model', path='/load',
                   description="Model Load API", cors_policy=cors_policy)

log = logging.getLogger(__name__)


@load_api.post()
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
    input_file = request.POST['new_model'].file

    # We first write to a temporary file to prevent incomplete files from
    # being used.
    file_name = '{0}.zip'.format(uuid.uuid4())
    file_path = os.path.join('/tmp', file_name)

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
