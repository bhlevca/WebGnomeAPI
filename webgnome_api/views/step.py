"""
Views for the Location objects.
"""
import sys
import traceback
import json

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPPreconditionFailed,
                                    HTTPUnprocessableEntity)
from cornice import Service

from webgnome_api.common.session_management import get_active_model

from webgnome_api.common.views import cors_policy

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
        except StopIteration:
            raise HTTPNotFound
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            fmt = traceback.format_exception(exc_type, exc_value,
                                             exc_traceback)

            http_exc = HTTPUnprocessableEntity()
            http_exc.json_body = json.dumps([l.strip() for l in fmt][-2:])
            raise http_exc
        finally:
            gnome_sema.release()

        return output
    else:
        http_exc = HTTPPreconditionFailed()
        raise http_exc


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
            exc_type, exc_value, exc_traceback = sys.exc_info()
            fmt = traceback.format_exception(exc_type, exc_value,
                                             exc_traceback)

            http_exc = HTTPUnprocessableEntity()
            http_exc.json_body = json.dumps([l.strip() for l in fmt][-2:])
            raise http_exc
        finally:
            gnome_sema.release()
    else:
        http_exc = HTTPPreconditionFailed()
        raise http_exc
