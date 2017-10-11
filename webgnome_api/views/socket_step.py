import re
import base64
import hashlib
import logging
import time

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


async_step_api = Service(name='async_step', path='/async_step',
                         description="Async Step API", cors_policy=cors_policy)
log = logging.getLogger(__name__)

socket_namespace = None

@async_step_api.get()
def run_model(request):
    '''
    Spawns a gevent greenlet that runs the model and writes the output to the
    web socket. Until interrupted using halt_model(), it will run to
    completion
    '''
    def execute_async_model(active_model, socket_namespace, request):
        '''
        Meant to run in a greenlet. This function should take an active model
        and run it, writing each step's output to the socket.
        b
        '''
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

            except:
                log.info('  ' + log_prefix + 'unknown exception...')
                raise cors_exception(request, HTTPUnprocessableEntity,
                                     with_stacktrace=True)
                break
            finally:
                #session_lock.release()
                #log.info('  {} session lock released (sess:{}, thr_id: {})'
                #         .format(log_prefix, id(session_lock),
                #                 current_thread().ident))
                #pdb.set_trace()
                if output:
                    socket_namespace.num_sent+=1
                    socket_namespace.emit('step', output)

            if not socket_namespace.is_async:
                socket_namespace.lock.clear()
                print 'lock!'
            socket_namespace.lock.wait()
            gevent.sleep(0.01)
        socket_namespace.emit('end')
        print 'broken out, greenlet ending?'

    print 'async_step route hit'
    ns = socket_namespace
    if ns is None:
        raise ValueError("socket is None")
    log_prefix = 'req{0}: run_model()'.format(id(request))
    log.info('>>' + log_prefix)
    active_model = get_active_model(request)
    if active_model and not ns.active_greenlet:
        ns.active_greenlet = ns.spawn(execute_async_model, active_model, socket_namespace, request)
        return None
    else:
        return "Already started"

def get_uncertain_steps(request):
    uncertain_models = get_uncertain_models(request)
    if uncertain_models:
        return uncertain_models.cmd('step', {})
    else:
        return None

class StepNamespace(BaseNamespace):
    def initialize(self):
        super(StepNamespace, self).initialize()
        print 'attaching namespace to module'
        global socket_namespace
        socket_namespace = self
        self.is_async = True
        self.lock = gevent.event.Event()
        self.lock.set()
        self.num_sent=0
        self.active_greenlet=None

    def recv_connect(self):
        print "STEP CONNNNNNNN"
        self.emit("step_started")
        socket_namespace = self

    def recv_disconnect(self):
        print "received disconnect signal"
        self.on_kill()
        self.lock.set()
        self.num_sent=0

    def on_halt(self):
        print 'halting'
        self.lock.clear()

    def on_kill(self):
        if self.active_greenlet:
            print 'killing greenlet {0}'.format(self.active_greenlet)
            self.active_greenlet.kill()
            print 'killed greenlet'

    def on_isAsync(self, b):
        self.is_async = bool(b)
        print 'setting async to {0}'.format(b)


    def on_ack(self, ack):
        if ack == self.num_sent:
            self.lock.set()
        print 'ack {0}'.format(ack)