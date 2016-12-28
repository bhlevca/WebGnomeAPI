"""
    Main entry point
"""
import os

import logging

import ujson
from pyramid.config import Configurator
from pyramid.renderers import JSON as JSONRenderer

from webgnome_api.common.views import cors_policy

logging.basicConfig()


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


def get_json(request):
    return ujson.loads(request.text)


def main(global_config, **settings):
    settings['package_root'] = os.path.abspath(os.path.dirname(__file__))
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

    config.add_request_method(get_json, 'json', reify=True)
    renderer = JSONRenderer(serializer=lambda v, **kw: ujson.dumps(v))
    config.add_renderer('json', renderer)
    config.add_tween('webgnome_api.tweens.PyGnomeSchemaTweenFactory')
    config.add_route("upload", "/upload")
    config.add_route("download", "/download")
    config.add_route("map_upload", "/map/upload")
    config.add_route("mover_upload", "/mover/upload")
    config.add_route("environment_upload", "/environment/upload")
    config.add_route("socket.io", "/socket.io/*remaining")
    config.add_route("export", "/export/*file_path")

    config.scan('webgnome_api.views')

    return config.make_wsgi_app()
