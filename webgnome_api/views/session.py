""" Cornice services.
"""
from webgnome_api.common.views import (cors_policy)

from cornice import Service


session = Service(name='session', path='/session', description="Session managment", cors_policy=cors_policy)


@session.post()
def get_info(request):
    request.session.changed()

    return {'id': request.cookies['session']}