"""
Views for the Location objects.
"""
from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPPreconditionFailed,
                                    HTTPUnprocessableEntity)
from cornice import Service

from webgnome_api.common.session_management import get_active_model

from webgnome_api.common.views import cors_exception, cors_policy

step_api = Service(name='step', path='/step',
                  description="Model Step API", cors_policy=cors_policy)
rewind_api = Service(name='rewind', path='/rewind',
                  description="Model Rewind API", cors_policy=cors_policy)


@step_api.get()
def get_step(request):
    '''
        Generates and returns an image corresponding to the step.
    '''
    active_model = get_active_model(request)
    if active_model:
        # generate the next step in the sequence.
        gnome_sema = request.registry.settings['py_gnome_semaphore']
        gnome_sema.acquire()

        try:
            output = active_model.step()
            low = output['WeatheringOutput']['0']
            high = output['WeatheringOutput']['0']
            for i, run in output['WeatheringOutput'].iteritems():
                if isinstance(run, dict):
                    if run['floating'] < low['floating']:
                        low = run

                    if run['floating'] > high['floating']:
                        high = run

            output['WeatheringOutput']['low'] = low
            output['WeatheringOutput']['high'] = high

        except StopIteration:
            raise cors_exception(request, HTTPNotFound)
        except:
            raise cors_exception(request, HTTPUnprocessableEntity,
                                 with_stacktrace=True)
        finally:
            gnome_sema.release()

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
