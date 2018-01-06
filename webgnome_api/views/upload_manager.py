"""
Views for the model load/save operations.
"""
import os
import errno
import logging
import urllib
import ujson

from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPBadRequest,
                                    HTTPUnauthorized,
                                    HTTPInternalServerError)

from cornice import Service

from ..common.helpers import PyObjFromJson
from ..common.system_resources import (list_files,
                                       file_info,
                                       mkdir,
                                       rename_or_move,
                                       remove_file_or_dir)
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
            raise cors_exception(request, HTTPInternalServerError)


@upload_manager.post()
@can_persist
def modify_filesystem(request):
    '''
        Make a file system modification within the uploads folder.
        Currently, we support the following actions:
        - create a new directory
        - rename a file
        - move a file into a directory (similar to renaming)
    '''
    sub_folders = [urllib.unquote(d).encode('utf8')
                   for d in request.matchdict['sub_folders']
                   if d != '..']

    base_path = get_persistent_dir(request)

    try:
        file_model = PyObjFromJson(ujson.loads(request.body))
    except Exception:
        raise cors_exception(request, HTTPBadRequest)

    if (file_model.type == 'd'):
        return create_new_folder(request, base_path, sub_folders, file_model)
    else:
        return rename_file(request, base_path, sub_folders, file_model)


@upload_manager.put()
@can_persist
def create_file_item(request):
    '''
        Make a new file folder or rename a previous file.
        When we started using the filename as a Backbone model id attribute,
        it started wanting to perform a PUT when we created a file model
        on the client.  In addition, it is performing a PUT when we rename
        a model. I suspect that since the filename is the identifier, it is
        performing a PUT of the new name, followed by a DELETE of the old one.

        So there are two operations we must support:
        - Create a new folder
        - Rename a file that already exists
    '''
    sub_folders = [urllib.unquote(d).encode('utf8')
                   for d in request.matchdict['sub_folders']
                   if d != '..']

    if len(sub_folders) == 0:
        log.error('PUT command should have the identifier in the url')
        raise cors_exception(request, HTTPBadRequest)

    base_path = get_persistent_dir(request)

    try:
        file_model = PyObjFromJson(ujson.loads(request.body))
    except Exception:
        log.error('PUT command payload could not be parsed')
        raise cors_exception(request, HTTPBadRequest)

    if sub_folders[-1] != file_model.name:
        log.error('PUT command payload should match the identifier in the url')
        raise cors_exception(request, HTTPBadRequest)

    if hasattr(file_model, 'prev_name'):
        log.info('create_file_item(): prev_name: {}'
                 .format(file_model.prev_name))
        return rename_file(request, base_path, sub_folders[:-1], file_model)
    elif (file_model.type == 'd'):
        return create_new_folder(request, base_path, sub_folders[:-1],
                                 file_model)
    else:
        print('unknown file type: {}'.format(file_model))
        raise cors_exception(request, HTTPBadRequest)


@upload_manager.delete()
@can_persist
def delete_uploaded_file(request):
    '''
        Performs a delete of a file in the uploads folder.
    '''
    sub_folders = [urllib.unquote(d).encode('utf8')
                   for d in request.matchdict['sub_folders']
                   if d != '..']

    requested_path = os.path.join(get_persistent_dir(request), *sub_folders)
    log.info('requesting delete of file: {}'.format(requested_path))

    try:
        remove_file_or_dir(requested_path)
    except OSError:
        raise cors_exception(request, HTTPInternalServerError)

    return {'message': 'File successfully deleted.'}


def create_new_folder(request, base_path, sub_folders, file_model):
    '''
        Create a new folder within the uploads folder.
    '''
    requested_path = os.path.join(base_path, *sub_folders)
    log.info('creating a new folder: {}'.format(file_model.name))

    try:
        mkdir(requested_path, file_model.name)
    except OSError:
        raise cors_exception(request, HTTPInternalServerError)

    return file_info(requested_path, file_model.name)


def rename_file(request, base_path, sub_folders, file_model):
    '''
        Rename a file within the uploads folder.
    '''
    if not validate_new_filename(file_model.name):
        log.info('new name failed validation: {}'.format(file_model.name))
        raise cors_exception(request, HTTPBadRequest)

    try:
        log.info('renaming file starts...')
        old_path = generate_new_path(base_path, [], file_model.prev_name)

        new_path = generate_new_path(base_path, sub_folders,
                                     file_model.name)

        log.info('renaming file from {} to {}'.format(old_path, new_path))

        rename_or_move(old_path, new_path)
    except Exception as e:
        log.info('Exception: {}'.format(e))
        raise cors_exception(request, HTTPInternalServerError)

    # Backbone.js likes to sync its models with the REST services it
    # communicates with.  So we need to return a model object that agrees
    # with what it expects when it performs a model.save() operation.
    # Otherwise, Backbone will treat it as a server-side change and perform
    # additional, and unwanted, requests.
    return {'name': file_model.name,
            'size': file_model.size,
            'type': file_model.type}


def validate_new_filename(name):
    '''
        When we rename a file, the allowed new name can be a single filename
        or a path.  The up-directory, '..', is not allowed.

        - 'filename': Good
        - 'folder1/folder2/filename': Good
        - '/folder1/folder2/filename': Good
        - '../../filename': Bad

        (Note: Here, we do not validate that the new path is valid on the
               filesystem, simply that the path has a valid syntactic form.)
    '''
    if name.find('..') > 0:
        return False

    return True


def generate_new_path(base_path, sub_folders, name):
    '''
        Generate a new full path name depending upon the syntactic properties
        of the new filename.
        Examples:
        - 'filename':                  base_path + sub_folders + name
        - 'folder1/folder2/filename':  base_path + sub_folders + name
        - '/folder1/folder2/filename': base_path + name
        - '../../filename':            shouldn't encounter this

    '''
    log.info('generate new path: {}, {}, {}'.format(base_path,
                                                    sub_folders,
                                                    name))

    if name.startswith(os.path.sep):
        # Absolute path
        # Note: os.path.join has a weird gotcha when joining absolute paths
        #       in that all previous paths are truncated.  Why anyone thought
        #       that was a good idea is beyond me.
        name = name[1:]
    else:
        # Filename or relative path
        base_path = os.path.join(base_path, *sub_folders)

    new_path = os.path.join(base_path, name)
    log.info('new path = {}'.format(new_path))

    return new_path
