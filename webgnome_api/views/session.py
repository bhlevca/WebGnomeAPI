""" Cornice services.
"""
from webgnome_api.common.views import (cors_policy)

from cornice import Service


session = Service(name='session', path='/session',
                  description="Session managment", cors_policy=cors_policy)


@session.post()
def get_info(request):
    gnome_sema = request.registry.settings['py_gnome_semaphore']
    gnome_sema.acquire()

    request.session.changed()

    gnome_sema.release()

    return {'id': request.cookies['session']}
