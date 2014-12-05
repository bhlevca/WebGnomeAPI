"""
    Main entry point
"""
import os
from threading import BoundedSemaphore

import logging
logging.basicConfig()

from pyramid.config import Configurator


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


def main(global_config, **settings):
    settings['package_root'] = os.path.abspath(os.path.dirname(__file__))
    settings['py_gnome_semaphore'] = BoundedSemaphore(value=1)
    settings['objects'] = {}
    settings['uncertain_models'] = {}

    reconcile_directory_settings(settings, 'data_dirs')

    config = Configurator(settings=settings)
    config.add_tween('webgnome_api.tweens.PyGnomeSchemaTweenFactory')
    config.scan('webgnome_api.views')

    return config.make_wsgi_app()
