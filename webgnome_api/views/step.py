"""
Views for the Location objects.
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from pyramid.httpexceptions import HTTPPreconditionFailed
from cornice import Service

from webgnome_api.common.common_object import get_active_model, obj_id_from_url
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
    active_model = get_active_model(request.session)
    if active_model:
        # generate the next step in the sequence.
        output = active_model.step()
        request.session.changed()
        return output
    else:
        http_exc = HTTPPreconditionFailed()
        raise http_exc


@rewind_api.get()
def get_rewind(request):
    '''
        rewinds the current active Model.
    '''
    active_model = get_active_model(request.session)
    if active_model:
        active_model.rewind()
        request.session.changed()
    else:
        http_exc = HTTPPreconditionFailed()
        raise http_exc
