"""
Views for the Location objects.
"""
import time
from collections import defaultdict
import logging
from threading import current_thread

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


step_api = Service(name='step', path='/step',
                   description="Model Step API", cors_policy=cors_policy)
full_run_api = Service(name='full_run', path='/full_run',
                       description="Model Full Run API",
                       cors_policy=cors_policy)

log = logging.getLogger(__name__)


@step_api.get()
def get_step(request):
    '''
        Generates and returns an image corresponding to the step.
    '''
    log_prefix = 'req({0}): get_step():'.format(id(request))
    log.info('>>' + log_prefix)

    active_model = get_active_model(request)
    if active_model:
        # generate the next step in the sequence.
        session_lock = acquire_session_lock(request)
        log.info('  {} session lock acquired (sess:{}, thr_id: {})'
                 .format(log_prefix, id(session_lock), current_thread().ident))

        try:
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
            raise cors_exception(request, HTTPNotFound)
        except Exception:
            log.info('  ' + log_prefix + 'unknown exception...')
            raise cors_exception(request, HTTPUnprocessableEntity,
                                 with_stacktrace=True)
        finally:
            session_lock.release()
            log.info('  {} session lock released (sess:{}, thr_id: {})'
                     .format(log_prefix, id(session_lock),
                             current_thread().ident))

        return output
    else:
        raise cors_exception(request, HTTPPreconditionFailed,
                             explanation=('Your session timed out '
                                          '- the model is no longer active'))


@full_run_api.post()
def get_full_run(request):
    '''
        Performs a full run of the current active Model, turning off any
        response options.
        Returns the final step results.
    '''

    response_on = request.json_body['response_on']

    active_model = get_active_model(request)
    if active_model:
        session_lock = acquire_session_lock(request)
        log.info('  session lock acquired (sess:{}, thr_id: {})'
                 .format(id(session_lock), current_thread().ident))

        try:
            weatherer_enabled_flags = [w.on for w in active_model.weatherers]

            if response_on is False:
                for w in active_model.weatherers:
                    if isinstance(w, (Skimmer, Burn, ChemicalDispersion)):
                        w.on = False

            active_model.rewind()

            drop_uncertain_models(request)

            if active_model.has_weathering_uncertainty:
                log.info('Model has weathering uncertainty')
                set_uncertain_models(request)
            else:
                log.info('Model does not have weathering uncertainty')

            begin = time.time()

            for step in active_model:
                output = step
                steps = get_uncertain_steps(request)

            end = time.time()

            if steps and 'WeatheringOutput' in output:
                nominal = output['WeatheringOutput']
                aggregate = defaultdict(list)
                low = {}
                high = {}
                full_output = {}

                for idx, step_output in enumerate(steps):
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
                output['total_response_time'] = end - begin
            elif 'WeatheringOutput' in output:
                nominal = output['WeatheringOutput']
                full_output = {'time_stamp': nominal['time_stamp'],
                               'nominal': nominal,
                               'low': None,
                               'high': None}
                output['WeatheringOutput'] = full_output
                output['total_response_time'] = end - begin

            active_model.rewind()
        except Exception:
            raise cors_exception(request, HTTPUnprocessableEntity,
                                 with_stacktrace=True)
        finally:
            for a, w in zip(weatherer_enabled_flags, active_model.weatherers):
                w.on = a
            session_lock.release()
            log.info('  session lock released (sess:{}, thr_id: {})'
                     .format(id(session_lock), current_thread().ident))

        return output
    else:
        raise cors_exception(request, HTTPPreconditionFailed)


def get_uncertain_steps(request):
    uncertain_models = get_uncertain_models(request)
    if uncertain_models:
        return uncertain_models.cmd('step', {})
    else:
        return None
