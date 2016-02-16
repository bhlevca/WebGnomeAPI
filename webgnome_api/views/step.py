"""
Views for the Location objects.
"""
import time
from collections import defaultdict
import logging

from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPPreconditionFailed,
                                    HTTPUnprocessableEntity)
from cornice import Service

from gnome.weatherers import Skimmer, Burn, ChemicalDispersion

from webgnome_api.common.session_management import (get_active_model,
                                                    get_uncertain_models,
                                                    drop_uncertain_models,
                                                    set_uncertain_models)

from webgnome_api.common.views import cors_exception, cors_policy


step_api = Service(name='step', path='/step',
                   description="Model Step API", cors_policy=cors_policy)
rewind_api = Service(name='rewind', path='/rewind',
                     description="Model Rewind API", cors_policy=cors_policy)
full_run_api = Service(name='full_run', path='/full_run_without_response',
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
        gnome_sema = request.registry.settings['py_gnome_semaphore']
        gnome_sema.acquire()
        log.info('  ' + log_prefix + 'semaphore acquired...')

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
        except:
            log.info('  ' + log_prefix + 'unknown exception...')
            raise cors_exception(request, HTTPUnprocessableEntity,
                                 with_stacktrace=True)
        finally:
            gnome_sema.release()
            log.info('  ' + log_prefix + 'semaphore released...')

        return output
    else:
        raise cors_exception(request, HTTPPreconditionFailed)


@rewind_api.get()
def get_rewind(request):
    '''
        rewinds the current active Model.
    '''
    active_model = get_active_model(request)
    if active_model:
        gnome_sema = request.registry.settings['py_gnome_semaphore']
        gnome_sema.acquire()

        try:
            active_model.rewind()
        except:
            raise cors_exception(request, HTTPUnprocessableEntity,
                                 with_stacktrace=True)
        finally:
            gnome_sema.release()
    else:
        raise cors_exception(request, HTTPPreconditionFailed)


@full_run_api.get()
def get_full_run(request):
    '''
        Performs a full run of the current active Model, turning off any
        response options.
        Returns the final step results.
    '''
    active_model = get_active_model(request)
    if active_model:
        gnome_sema = request.registry.settings['py_gnome_semaphore']
        gnome_sema.acquire()

        try:
            weatherer_active_flags = [w.active
                                      for w in active_model.weatherers]
            for w in active_model.weatherers:
                if isinstance(w, (Skimmer, Burn, ChemicalDispersion)):
                    w._active = False

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
        except:
            raise cors_exception(request, HTTPUnprocessableEntity,
                                 with_stacktrace=True)
        finally:
            for a, w in zip(weatherer_active_flags, active_model.weatherers):
                w._active = a
            gnome_sema.release()

        return output
    else:
        raise cors_exception(request, HTTPPreconditionFailed)


def get_uncertain_steps(request):
    uncertain_models = get_uncertain_models(request)
    if uncertain_models:
        return uncertain_models.cmd('step', {})
    else:
        return None
