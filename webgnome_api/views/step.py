"""
Views for the Location objects.
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from pyramid.httpexceptions import HTTPPreconditionFailed
from cornice import Service

from webgnome_api.common.common_object import get_active_model, obj_id_from_url
from webgnome_api.common.views import cors_policy

step_api = Service(name='step', path='/step*obj_id',
                  description="Model Step API", cors_policy=cors_policy)


@step_api.get()
def get_step(request):
    '''
        Generates and returns an image corresponding to the step.
    '''
    active_model = get_active_model(request.session)
    if active_model:
        step_id = obj_id_from_url(request)
        if step_id:
            # generate the image corresponding to the step
            pass
        else:
            # generate the first image in the sequence.
            image_info = active_model.step()
            print 'image_info:'
            pp.pprint(image_info)
            pass
        # return the url to the image.
        return {'url': 'http://www.domain.com/step.png'}
    else:
        http_exc = HTTPPreconditionFailed()
        raise http_exc
