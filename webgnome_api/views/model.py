"""
Views for the Model object.
"""

from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPUnsupportedMediaType)
from cornice import Service

from webgnome_api.common.views import (create_object,
                                       update_object,
                                       cors_policy,
                                       get_session_object,
                                       obj_id_from_url)
from webgnome_api.common.common_object import (ObjectImplementsOneOf,
                                               set_session_object)

model = Service(name='model', path='/model*obj_id', description="Model API",
                cors_policy=cors_policy)

import gnome
from gnome.model import Model
implemented_types = ('gnome.model.Model',
                     )


@model.get()
def get_model(request):
    '''
        Returns Model object in JSON.
        - This method varies slightly from the common object method in that
          if we don't specify a model ID, we:
          - return the current active model if it exists or...
          - create a new blank model and return it.
    '''
    obj_id = obj_id_from_url(request)
    if not obj_id:
        my_model = get_active_model(request.session)
        if my_model:
            return my_model.serialize()
        else:
            # - create a new blank model
            # - add it to the session objects
            # - add its map to the session objects
            # - set it to the active_model
            # = return it
            new_model = Model()
            #new_model = eval('{0}()'.format(implemented_types[0]))
            set_session_object(new_model, request.session)
            set_session_object(new_model._map, request.session)
            set_active_model(request.session, new_model.id)
            return new_model.serialize()
    else:
        obj = get_session_object(obj_id, request.session)
        if obj:
            if ObjectImplementsOneOf(obj, implemented_types):
                set_active_model(request.session, obj.id)
                return obj.serialize()
            else:
                raise HTTPUnsupportedMediaType()
        else:
            raise HTTPNotFound()


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
