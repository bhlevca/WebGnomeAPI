"""
Common Gnome object request handlers.
"""
from gnome.multi_model_broadcast import ModelBroadcaster


def init_session_objects(request, force=False):
    session = request.session
    obj_pool = request.registry.settings['objects']

    if (session.session_id not in obj_pool) or force:
        obj_pool[session.session_id] = {}


def get_session_objects(request):
    init_session_objects(request)
    obj_pool = request.registry.settings['objects']

    return obj_pool[request.session.session_id]


def get_session_object(obj_id, request):
    objects = get_session_objects(request)
    return objects.get(obj_id, None)


def set_session_object(obj, request):
    objects = get_session_objects(request)

    try:
        objects[obj.id] = obj
    except AttributeError:
        objects[id(obj)] = obj


def set_active_model(request, obj_id):
    session = request.session

    if not ('active_model' in session and
            session['active_model'] == obj_id):
        session['active_model'] = obj_id
        session.changed()


def get_active_model(request):
    session = request.session

    if 'active_model' in session and session['active_model']:
        return get_session_object(session['active_model'], request)
    else:
        return None


def get_uncertain_models(request):
    session_id = request.session.session_id
    uncertainty_models = request.registry.settings['uncertain_models']

    if session_id in uncertainty_models:
        return uncertainty_models[session_id]
    else:
        return None


def set_uncertain_models(request):
    session_id = request.session.session_id
    uncertain_models = request.registry.settings['uncertain_models']

    active_model = get_active_model(request)
    if active_model:
        model_broadcaster = ModelBroadcaster(active_model,
                                             ('down', 'normal', 'up'),
                                             ('down', 'normal', 'up'),
                                             'ipc_files')

        uncertain_models[session_id] = model_broadcaster


def drop_uncertain_models(request):
    session_id = request.session.session_id
    uncertain_models = request.registry.settings['uncertain_models']

    if (session_id in uncertain_models and
            uncertain_models[session_id] is not None):
        uncertain_models[session_id].stop()
        uncertain_models[session_id] = None
