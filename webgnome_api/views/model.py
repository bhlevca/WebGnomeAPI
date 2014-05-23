"""
Views for the Model object.
"""

from pyramid.httpexceptions import HTTPNotFound
from cornice import Service

from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy,
                                       get_session_object,
                                       obj_id_from_url)

model = Service(name='model', path='/model*obj_id', description="Model API",
                cors_policy=cors_policy)

implemented_types = ('gnome.model.Model',
                     )


@model.get()
def get_model(request):
    '''
        Returns Model object in JSON.
        - This method varies slightly from the common object method in that
          if we don't specify a model ID, we return the current active model.
    '''
    try:
        return get_object(request, implemented_types)
    except HTTPNotFound:
        if obj_id_from_url(request):
            raise

        my_model = get_active_model(request.session)
        if my_model:
            return my_model.serialize()
        else:
            raise


@model.post()
def create_model(request):
    resp = create_object(request, implemented_types)
    set_active_model(request.session, resp['id'])
    return resp


@model.put()
def update_model(request):
    resp = update_object(request, implemented_types)
    set_active_model(request.session, resp['id'])
    return resp


def get_active_model(session):
    if 'active_model' in session and session['active_model']:
        return get_session_object(session['active_model'], session)
    else:
        return None


def set_active_model(session, obj_id):
    if not ('active_model' in session and
            session['active_model'] == obj_id):
        session['active_model'] = obj_id
        session.changed()
