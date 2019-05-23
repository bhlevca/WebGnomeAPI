"""
    Main entry point
"""
import os
import shutil
import logging

import ujson
import gevent

from redis import StrictRedis

from pyramid.config import Configurator
from pyramid.renderers import JSON as JSONRenderer
from pyramid.threadlocal import get_current_request
from pyramid_log import Formatter, _WrapDict, _DottedLookup

from pyramid_redis_sessions import session_factory_from_settings

from webgnome_api.common.views import cors_policy

logging.basicConfig()


class WebgnomeFormatter(Formatter):
    def format(self, record):
        # Format the specific record as text.
        has_session_hash = hasattr(record, 'session_hash')
        if not has_session_hash:
            record.session_hash = '<no session>'
            gvt = gevent.getcurrent()
            gvt_session_hash = (isinstance(gvt, gevent.Greenlet) and
                                hasattr(gvt, 'session_hash'))

            if gvt_session_hash:
                record.session_hash = gvt.session_hash
            else:
                request = get_current_request()

                if request is not None:
                    record.session_hash = request.session_hash

        # magic_record.__dict__ support dotted attribute lookup

        magic_record = _WrapDict(record, _DottedLookup)

        # Disable logging during disable to prevent recursion (in case
        # a logged request property generates a log message)
        save_disable = logging.root.manager.disable
        logging.disable(record.levelno)

        try:
            return logging.Formatter.format(self, magic_record)
        finally:
            logging.disable(save_disable)

            if not has_session_hash and hasattr(record, 'session_hash'):
                del record.session_hash


class DummySession(object):
    session_id = 'DummySession'


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
    return ujson.loads(request.text, ensure_ascii=False)


def overload_redis_session_factory(settings, config):
    '''
        pyramid_redis_sessions will create a session object for every request,
        even the CORS preflight requests, and if there is no session cookie,
        a new session key will be created.  And the CORS preflight requests
        will never have a session cookie.  So we overload the session factory
        function here and add a special case for CORS preflight requests.
    '''
    session_factory = session_factory_from_settings(settings)

    def overloaded_session_factory(request, **kwargs):
        if request.method.lower() == 'options':
            return DummySession()
        else:
            return session_factory(request, **kwargs)

    config.set_session_factory(overloaded_session_factory)


def start_session_cleaner(settings):
    '''
        When a session expires, we need to cleanup the session folder that was
        created for it, but pyramid_redis_sessions has no builtin way to add
        or register custom functions to do this.
        So we need to hook directly into the Redis publish/subscribe
        functionality.  Here we will look for expired key events.
    '''
    host = settings.get('redis.sessions.host', 'localhost')
    port = int(settings.get('redis.sessions.port', 6379))
    session_dir = settings.get('session_dir', './models/session')

    redis = StrictRedis(host=host, port=port)

    def event_handler(msg, session_dir=session_dir):
        cleanup_dir = os.path.join(session_dir, msg['data'])

        try:
            shutil.rmtree(cleanup_dir)
        except OSError as err:
            if err.errno == 2:  # not-found error.  Print message & continue.
                print ('Session Cleaner: Folder {} does not exist!'
                       .format(cleanup_dir))
            else:
                raise

    pubsub = redis.pubsub()
    pubsub.psubscribe(**{'__keyevent*__:expired': event_handler})

    settings['redis_pubsub_thread'] = pubsub.run_in_thread(sleep_time=60.0, daemon=True)


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
    start_session_cleaner(settings)

    config = Configurator(settings=settings)

    overload_redis_session_factory(settings, config)

    # we use ujson to load our JSON payloads
    config.add_request_method(get_json, 'json', reify=True)

    renderer = JSONRenderer(serializer=lambda v, **kw: ujson.dumps(v))
    config.add_renderer('json', renderer)

    config.add_tween('webgnome_api.tweens.PyGnomeSchemaTweenFactory')

    config.add_route('upload', '/upload')
    config.add_route('activate', '/activate')
    config.add_route('download', '/download')
    config.add_route('persist', '/persist')

    config.add_route('map_upload', '/map/upload')
    config.add_route('map_activate', '/map/activate')

    config.add_route('mover_upload', '/mover/upload')

    config.add_route('environment_upload', '/environment/upload')
    config.add_route('environment_activate', '/environment/activate')

    config.add_route('socket.io', '/socket.io/*remaining')
    config.add_route('logger', '/logger')
    config.add_route('export', '/export/*file_path')

    config.scan('webgnome_api.views')

    return config.make_wsgi_app()
