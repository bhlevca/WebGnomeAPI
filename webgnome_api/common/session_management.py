"""
Common Gnome object request handlers.
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


def init_session_objects(request, force=False):
    session = request.session
    obj_pool = request.registry.settings['objects']

    if (not session.session_id in obj_pool) or force:
        print ('init_session_objects(): '
               'initializing object dict.')
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
