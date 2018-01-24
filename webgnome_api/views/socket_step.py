import re
import base64
import hashlib
import logging
import time
import traceback
import sys
from threading import current_thread

from pygtail import Pygtail

from pyramid.view import view_config

import gevent
from gevent import socket

from socketio import socketio_manage
from socketio.namespace import BaseNamespace

from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPPreconditionFailed,
                                    HTTPUnprocessableEntity)
from cornice import Service

from gnome.weatherers import Skimmer, Burn, ChemicalDispersion

from webgnome_api.common.session_management import (get_active_model,
                                                    get_uncertain_models,
                                                    drop_uncertain_models,
                                                    set_uncertain_models,
                                                    acquire_session_lock)

from webgnome_api.common.views import cors_exception, cors_policy
from greenlet import GreenletExit


async_step_api = Service(name='async_step', path='/async_step',
                         description="Async Step API", cors_policy=cors_policy)

rewind_api = Service(name='rewind', path='/rewind',
                     description="Model Rewind API", cors_policy=cors_policy)
log = logging.getLogger(__name__)

socket_namespace = None

sess_namespaces = {}

@async_step_api.get()
def run_model(request):
    '''
    Spawns a gevent greenlet that runs the model and writes the output to the
    web socket. Until interrupted using halt_model(), it will run to
    completion
    '''
    sess_id = request.session.session_id
    global sess_namespaces
    ns = sess_namespaces.get(sess_id, None)
    if ns is None:
        raise ValueError('no namespace associated with session')

    def execute_async_model(active_model, socket_namespace, request):
        '''
        Meant to run in a greenlet. This function should take an active model
        and run it, writing each step's output to the socket.
        b
        '''
        try:
            w = 6
            socket_namespace.emit('prepared')
            unlocked = socket_namespace.lock.wait(w)
            if not unlocked:
                socket_namespace.emit('timeout', 'Model not started, timed out after {0} sec'.format(w))
                socket_namespace.on_kill()
            log.info('model run triggered')
            while True:
                output = None
                try:
                    #pdb.set_trace()
                    if active_model.current_time_step == -1:
                        # our first step, establish uncertain models
                        drop_uncertain_models(request)

                        log.info('\thas_weathering_uncertainty {0}'.
                                 format(active_model.has_weathering_uncertainty))
                        if active_model.has_weathering_uncertainty:
                            set_uncertain_models(request)
                        else:
                            log.info('Model does not have weathering uncertainty')

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
                            # we should propagate the exception with its original
                            # context.
                            if (isinstance(step_output, tuple) and
                                    len(step_output) >= 3 and
                                    isinstance(step_output[1], Exception)):
                                raise step_output[1], None, step_output[2]

                            for k, v in step_output['WeatheringOutput'].iteritems():
                                aggregate[k].append(v)

                        for k, v in aggregate.iteritems():
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
                    log.info('  ' + log_prefix + 'stop iteration exception...')
                    drop_uncertain_models(request)
                    break

                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    log.critical('  ' + log_prefix + str(traceback.format_exception_only(exc_type, exc_value)))
                    socket_namespace.emit('killed', 'Model run terminated early')
                    return
                finally:
                    #session_lock.release()
                    #log.info('  {} session lock released (sess:{}, thr_id: {})'
                    #         .format(log_prefix, id(session_lock),
                    #                 current_thread().ident))
                    #pdb.set_trace()
                    if output:
                        socket_namespace.num_sent+=1
                        log.debug(socket_namespace.num_sent)
                        socket_namespace.emit('step', output)

                if not socket_namespace.is_async:
                    socket_namespace.lock.clear()
                    print 'lock!'
                #kill greenlet after 100 minutes unless unlocked
                w = 6000
                unlocked = socket_namespace.lock.wait(w)
                if not unlocked:
                    socket_namespace.emit('timeout', 'Model run timed out after {0} sec'.format(w))
                    socket_namespace.on_kill()
                gevent.sleep(0.001)
        except GreenletExit:
            log.info('Greenlet exiting early')
            socket_namespace.emit('killed', 'Model run terminated early')
        socket_namespace.emit('complete', 'Model run completed')

    print 'async_step route hit'
    #ns = socket_namespace
    #if ns is None:
    #    raise ValueError("socket is None")
    log_prefix = 'req{0}: run_model()'.format(id(request))
    log.info('>>' + log_prefix)
    active_model = get_active_model(request)
    if active_model and not ns.active_greenlet:
        ns.active_greenlet = ns.spawn(execute_async_model, active_model, ns, request)
        return None
    else:
        print "Already started"
        return None

def get_uncertain_steps(request):
    uncertain_models = get_uncertain_models(request)
    if uncertain_models:
        return uncertain_models.cmd('step', {})
    else:
        return None

class StepNamespace(BaseNamespace):
    inst_count=0
    def initialize(self):
        super(StepNamespace, self).initialize()
        print 'attaching namespace to module'
        global sess_namespaces
        sess_namespaces[self.request.session.session_id] = self
        print self.request.session.session_id
        self.is_async = True
        self.lock = gevent.event.Event()
        self.lock.clear()
        self.num_sent=0
        self.active_greenlet=None
        self.inst = StepNamespace.inst_count
        StepNamespace.inst_count += 1

    def recv_connect(self):
        print "STEP CONNNNNNNN"
        print self.inst
        self.emit("step_started")
        socket_namespace = self

    def recv_disconnect(self):
        print "received disconnect signal"
        self.num_sent=0
        #super(StepNamespace, self).recv_disconnect()

    def on_halt(self):
        print 'halting', self.request.session.session_id
        self.lock.clear()

    def on_kill(self):
        if self.active_greenlet:
            print 'killing greenlet {0}'.format(self.active_greenlet)
            self.active_greenlet.kill(block=False)
            self.emit('killed', 'Model run terminated')
            print 'killed greenlet'
            self.num_sent=0

    def on_isAsync(self, b):
        self.is_async = bool(b)
        print 'setting async to {0}'.format(b)


    def on_ack(self, ack):
        if ack == self.num_sent:
            self.lock.set()
        print 'ack {0}'.format(ack)


@rewind_api.get()
def get_rewind(request):
    '''
        rewinds the current active Model.
    '''
    print 'rewinding', request.session.session_id
    active_model = get_active_model(request)
    ns = sess_namespaces.get(request.session.session_id, None)
    if active_model:
        session_lock = acquire_session_lock(request)
        log.info('  session lock acquired (sess:{}, thr_id: {})'
                 .format(id(session_lock), current_thread().ident))

        try:
            active_model.rewind()
            if (ns and ns.active_greenlet):
                ns.on_kill()
        except:
            raise cors_exception(request, HTTPUnprocessableEntity,
                                 with_stacktrace=True)
        finally:
            session_lock.release()
            log.info('  session lock released (sess:{}, thr_id: {})'
                     .format(id(session_lock), current_thread().ident))
    else:
        raise cors_exception(request, HTTPPreconditionFailed)