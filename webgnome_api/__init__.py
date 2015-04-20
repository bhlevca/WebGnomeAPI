"""
    Main entry point
"""
import os
from threading import BoundedSemaphore

import logging
logging.basicConfig()

from pyramid.config import Configurator

from webgnome_api.common.views import cors_policy


def reconcile_directory_settings(settings):
    save_file_dir = settings['save_file_dir']

    for d in (save_file_dir,):
        if not os.path.exists(d):
            print 'Creating folder {0}'.format(d)
            os.mkdir(d)
        elif not os.path.isdir(d):
            raise EnvironmentError('Folder path {0} '
                                   'is not a directory!!'.format(d))

    locations_dir = settings['locations_dir']

    if not os.path.exists(locations_dir):
        raise EnvironmentError('Location files folder path {0} '
                               'does not exist!!'.format(locations_dir))
    if not os.path.isdir(locations_dir):
        raise EnvironmentError('Location files folder path {0} '
                               'is not a directory!!'.format(locations_dir))


def load_cors_origins(settings, key):
    if key in settings:
        origins = settings[key].split('\n')
        cors_policy['origins'] = origins


def main(global_config, **settings):
    settings['package_root'] = os.path.abspath(os.path.dirname(__file__))
    settings['py_gnome_semaphore'] = BoundedSemaphore(value=1)
    settings['objects'] = {}

    settings['uncertain_models'] = {}
    try:
        os.mkdir('ipc_files')
    except OSError, e:
        # it is ok if the folder already exists.
        if e.errno != 17:
            raise

    reconcile_directory_settings(settings)
    load_cors_origins(settings, 'cors_policy.origins')

    config = Configurator(settings=settings)
    config.add_tween('webgnome_api.tweens.PyGnomeSchemaTweenFactory')
    config.add_route("upload", "/upload")
    config.add_route("download", "/download")
    config.add_route("logger", "/logger")

    config.scan('webgnome_api.views')

    return config.make_wsgi_app()
