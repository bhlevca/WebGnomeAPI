"""
    Main entry point
"""
import os
from threading import BoundedSemaphore

import logging
logging.basicConfig()

from pyramid.config import Configurator

from webgnome_api.common.views import cors_policy


def reconcile_directory_settings(settings, key):
    if key in settings:
        data_dirs = settings[key].split('\n')

        resolved_dirs = [p for p in data_dirs if os.path.isdir(p)]
        if resolved_dirs:
            print 'We will use the following data directories:\n\t',
            print '\n\t'.join(resolved_dirs), '\n'

        settings[key] = '\n'.join(resolved_dirs)
    else:
        # print 'Warning: key {0} not found in settings.'.format(key)
        pass


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

    reconcile_directory_settings(settings, 'data_dirs')
    load_cors_origins(settings, 'cors_policy.origins')

    config = Configurator(settings=settings)
    config.add_tween('webgnome_api.tweens.PyGnomeSchemaTweenFactory')
    config.scan('webgnome_api.views')

    return config.make_wsgi_app()
