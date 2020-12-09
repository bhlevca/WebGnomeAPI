import sys
import time
import logging
import ujson
import tempfile
import os
import zipfile
import shutil

import traceback
from collections import defaultdict
from threading import current_thread

import gevent

from socketio.namespace import BaseNamespace
from pyramid.response import FileResponse

from pyramid.httpexceptions import (HTTPPreconditionFailed,
                                    HTTPUnprocessableEntity,
                                    HTTPNotFound)
from cornice import Service
from greenlet import GreenletExit

from webgnome_api.common.common_object import (CreateObject,
                                               get_session_dir)

from webgnome_api.common.session_management import (get_active_model,
                                                    get_uncertain_models,
                                                    drop_uncertain_models,
                                                    set_uncertain_models,
                                                    acquire_session_lock,
                                                    get_session_objects)

from webgnome_api.common.views import (cors_exception,
                                       cors_policy,
                                       cors_response,
                                       json_exception)

async_step_api = Service(name='async_step', path='/async_step',
                         description="Async Step API", cors_policy=cors_policy)

rewind_api = Service(name='rewind', path='/rewind',
                     description="Model Rewind API", cors_policy=cors_policy)

export_api = Service(name='ws_export', path='/ws_export*',
    description = "Websocket export API", cors_policy=cors_policy,
    content_type=['application/json'])

sess_namespaces = {}

log = logging.getLogger(__name__)

class GnomeRuntimeError(Exception):
    pass


def get_greenlet_logger(request):
    adpt = logging.LoggerAdapter(log, {'request': request})
    return adpt

@export_api.get()
def get_output_file(request):
    log_prefix = 'req{0}: get_output_file()'.format(id(request))
    log.info('>>' + log_prefix)
    session_path = get_session_dir(request)
    filename = request.GET.get('filename')
    if filename:
        output_path = os.path.join(session_path, filename)

        response = FileResponse(output_path, request)
        response.headers['Content-Disposition'] = ("attachment; filename={0}"
                                                    .format(os.path.basename(output_path)))
        log.info('<<' + log_prefix)
        return response
    else:
        raise cors_response(request, HTTPNotFound('File(s) requested do not '
                                                  'exist on the server!'))



@export_api.put()
def run_export_model(request):
    '''
    Configures the active model as specified by the request, then
    spawns a gevent greenlet that runs the model, writing only step number
    to the web socket.

    When the greenlet running the model dies, it removes the outputters that were added
    via a linked function
    '''
    print('async export hit')
    log_prefix = 'req{0}: run_export_model()'.format(id(request))
    log.info('>>' + log_prefix)

    sess_id = request.session.session_id
    global sess_namespaces

    ns = sess_namespaces.get(sess_id, None)
    if ns is None:
        raise ValueError('no namespace associated with session')
    
    active_model = get_active_model(request)

    #setup temporary outputters and temporary output directory
    session_path = get_session_dir(request)
    temporary_outputters = []
    payload = ujson.loads(request.body)
    outpjson = payload['outputters']
    model_filename = payload['model_name']
    td = tempfile.mkdtemp()
    for itm in list(outpjson.values()):
        itm['filename'] = os.path.join(td, itm['filename'])
        obj = CreateObject(itm, get_session_objects(request))
        temporary_outputters.append(obj)
    for o in temporary_outputters:
        #separated these just in case an exception occurs when
        #creating an outputter, which may leave a different successfully added
        #outputter behind if one was created before the exception
        active_model.outputters += o
        log.info('attaching export outputter: ' + o.filename)

    def get_export_cleanup():
        def cleanup(grn):
            try :
                #remove outputters from the model
                num = 0
                for m in temporary_outputters:
                    active_model.outputters.remove(m.id)
                    num += 1
                active_model.rewind()
                log.info(grn.__repr__() + ': cleaned up ' + str(num) + ' outputters')

                end_filename = None
                if (grn.exception or isinstance(grn.value, GreenletExit)):
                    #A cleanly stopped Greenlet may exit with GreenletExit
                    #Do not consider this a 'successful' export run even if files exist
                    ns.emit('export_failed')
                else:
                    if len(temporary_outputters) > 1:
                        #need to zip up outputs
                        end_filename = model_filename + '_output.zip'
                        zipfile_ = zipfile.ZipFile(os.path.join(session_path, end_filename), 'w',
                                                compression=zipfile.ZIP_DEFLATED)
                        for m in temporary_outputters:
                            obj_fn = m.filename
                            if not os.path.exists(obj_fn):
                                obj_fn = obj_fn + '.zip' #special case for shapefile outputter which strips extensions...
                            zipfile_.write(obj_fn, os.path.basename(obj_fn))
                    else:
                        #only one output file, because one outputter selected
                        obj_fn = temporary_outputters[0].filename
                        if not os.path.exists(obj_fn):
                            obj_fn = obj_fn + '.zip' #special case for shapefile outputter
                        end_filename = os.path.basename(obj_fn)

                        shutil.move(obj_fn, os.path.join(session_path, end_filename))

                    ns.emit('export_finished', end_filename)

            except Exception:
                if ('develop_mode' in list(request.registry.settings.keys()) and
                            request.registry.settings['develop_mode'].lower() == 'true'):
                    import pdb
                    pdb.post_mortem(sys.exc_info()[2])
                raise
        return cleanup

    if active_model and not ns.active_greenlet:
        ns.active_greenlet = ns.spawn(execute_async_model, active_model,
                                      ns, request, False)
        ns.active_greenlet.session_hash = request.session_hash
        ns.active_greenlet.link(get_export_cleanup())
        return None
    else:
        print("Already started")
        return None



@async_step_api.get()
def run_model(request):
    '''
    Spawns a gevent greenlet that runs the model and writes the output to the
    web socket. Until interrupted using halt_model(), it will run to
    completion
    '''
    print('async_step route hit')
    log_prefix = 'req{0}: run_model()'.format(id(request))
    log.info('>>' + log_prefix)

    sess_id = request.session.session_id
    global sess_namespaces

    ns = sess_namespaces.get(sess_id, None)
    if ns is None:
        raise ValueError('no namespace associated with session')
    
    active_model = get_active_model(request)
    if active_model and not ns.active_greenlet:
        ns.active_greenlet = ns.spawn(execute_async_model, active_model,
                                      ns, request)
        ns.active_greenlet.session_hash = request.session_hash
        return None
    else:
        print("Already started")
        return None


def execute_async_model(
    active_model=None,
    socket_namespace=None,
    request=None,
    send_output=True
    ):
    '''
    Meant to run in a greenlet. This function should take an active model
    and run it, writing each step's output to the socket.
    '''
    print(request.session_hash)
    log = get_greenlet_logger(request)
    log_prefix = 'req{0}: execute_async_model()'.format(id(request))
    try:
        wait_time = 16
        socket_namespace.emit('prepared')

        unlocked = socket_namespace.lock.wait(wait_time)
        if not unlocked:
            socket_namespace.emit('timeout',
                                    'Model not started, timed out after '
                                    '{0} sec'.format(wait_time))
            socket_namespace.on_kill()

        log.info('model run triggered')
        while True:
            output = None
            try:
                if active_model.current_time_step == -1:
                    # our first step, establish uncertain models
                    drop_uncertain_models(request)

                    if active_model.has_weathering_uncertainty:
                        log.info('Model has weathering uncertainty')
                        set_uncertain_models(request)
                    else:
                        log.info('Model does not have '
                                    'weathering uncertainty')

                begin = time.time()

                output = active_model.step()

                begin_uncertain = time.time()
                steps = get_uncertain_steps(request)
                end = time.time()

                if steps and 'WeatheringOutput' in output:
                    nominal = output['WeatheringOutput']
                    aggregate = defaultdict(list)
                    low = {}
                    high = {}
                    full_output = {}

                    for idx, step_output in enumerate(steps):
                        # step_output could contain an exception from one
                        # of our uncertainty worker processes.  If so, then
                        # we should propagate the exception with its
                        # original context.
                        if (isinstance(step_output, tuple) and
                                len(step_output) >= 3 and
                                isinstance(step_output[1], Exception)):
                            raise step_output[1].with_traceback(step_output[2])

                        for k, v in step_output['WeatheringOutput'].items():
                            aggregate[k].append(v)

                    for k, v in aggregate.items():
                        low[k] = min(v)
                        high[k] = max(v)

                    full_output = {'time_stamp': nominal['time_stamp'],
                                    'nominal': nominal,
                                    'low': low,
                                    'high': high}

                    for idx, step_output in enumerate(steps):
                        full_output[idx] = step_output['WeatheringOutput']

                    output['WeatheringOutput'] = full_output
                    output['uncertain_response_time'] = end - begin_uncertain
                    output['total_response_time'] = end - begin
                elif 'WeatheringOutput' in output:
                    nominal = output['WeatheringOutput']
                    full_output = {'time_stamp': nominal['time_stamp'],
                                    'nominal': nominal,
                                    'low': None,
                                    'high': None}

                    output['WeatheringOutput'] = full_output
                    output['uncertain_response_time'] = end - begin_uncertain
                    output['total_response_time'] = end - begin
            except StopIteration:
                log.info('  {} stop iteration exception...'
                            .format(log_prefix))
                drop_uncertain_models(request)
                break
            except Exception:
                exc_type, exc_value, _exc_traceback = sys.exc_info()
                traceback.print_exc()
                if ('develop_mode' in list(request.registry.settings.keys()) and
                            request.registry.settings['develop_mode'].lower() == 'true'):
                    import pdb
                    pdb.post_mortem(sys.exc_info()[2])

                msg = ('  {}{}'
                        .format(log_prefix, traceback.format_exception_only(exc_type,
                                                                exc_value)))
                log.critical(msg)
                raise   

            socket_namespace.num_sent += 1
            log.debug(socket_namespace.num_sent)
            if output and send_output:
                socket_namespace.emit('step', output)
            else:
                socket_namespace.emit('step', socket_namespace.num_sent)

            if not socket_namespace.is_async:
                socket_namespace.lock.clear()
                print('lock!')

            # kill greenlet after 100 minutes unless unlocked
            wait_time = 6000
            unlocked = socket_namespace.lock.wait(wait_time)
            if not unlocked:
                socket_namespace.emit('timeout',
                                        'Model run timed out after {0} sec'
                                        .format(wait_time))
                socket_namespace.on_kill()

            gevent.sleep(0.001)
    except GreenletExit:
        log.info('Greenlet exiting early')
        socket_namespace.emit('killed', 'Model run terminated early')
        raise

    except Exception:
        log.info('Greenlet terminated due to exception')

        json_exc = json_exception(2, True)
        socket_namespace.emit('runtimeError', json_exc['message'])
        raise

    socket_namespace.emit('complete', 'Model run completed')




def get_uncertain_steps(request):
    uncertain_models = get_uncertain_models(request)
    if uncertain_models:
        return uncertain_models.cmd('step', {})
    else:
        return None


class StepNamespace(BaseNamespace):
    inst_count = 0

    def initialize(self):
        super(StepNamespace, self).initialize()
        print(('attaching namespace {} to module'
               .format(self.__class__.__name__)))

        global sess_namespaces
        sess_namespaces[self.request.session.session_id] = self
        print(self.request.session.session_id)

        self.is_async = True
        self.lock = gevent.event.Event()
        self.lock.clear()
        self.num_sent = 0
        self.active_greenlet = None

        self.inst = StepNamespace.inst_count
        StepNamespace.inst_count += 1

    def recv_connect(self):
        log.debug("STEP CONNNNNNNN")
        log.debug(self.inst)
        self.emit("step_started")

    def recv_disconnect(self):
        log.debug("received disconnect signal")
        self.num_sent = 0

    def on_halt(self):
        log.debug('halting {0}'.format(self.request.session.session_id))
        self.lock.clear()

    def on_kill(self):  # kill signal from client
        if self.active_greenlet:
            log.debug('killing greenlet {0}'.format(self.active_greenlet))
            self.active_greenlet.kill(block=True, timeout=5)
            self.emit('killed', 'Model run terminated')
            log.debug('killed greenlet {0}'.format(self.active_greenlet))
            self.num_sent = 0

    def on_isAsync(self, b):
        self.is_async = bool(b)
        print('setting async to {0}'.format(b))

    def on_ack(self, ack):
        if ack == self.num_sent:
            self.lock.set()
        print('ack {0}'.format(ack))


@rewind_api.get()
def get_rewind(request):
    '''
        rewinds the current active Model.
    '''
    print('rewinding', request.session.session_id)
    active_model = get_active_model(request)
    ns = sess_namespaces.get(request.session.session_id, None)
    if active_model:
        session_lock = acquire_session_lock(request)
        log.info('  session lock acquired (sess:{}, thr_id: {})'
                 .format(id(session_lock), current_thread().ident))

        try:
            if (ns and ns.active_greenlet):
                ns.active_greenlet.kill(block=False)
                ns.num_sent = 0
            active_model.rewind()
        except Exception:
            raise cors_exception(request, HTTPUnprocessableEntity,
                                 with_stacktrace=True)
        finally:
            session_lock.release()
            log.info('  session lock released (sess:{}, thr_id: {})'
                     .format(id(session_lock), current_thread().ident))
    else:
        raise cors_exception(request, HTTPPreconditionFailed)
