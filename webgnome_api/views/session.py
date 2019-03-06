""" Cornice services.
"""
from cornice import Service

from webgnome_api.common.views import cors_policy


session = Service(name='session', path='/session',
                  description="Session managment", cors_policy=cors_policy)


@session.post()
def get_info(request):
    request.session.redis.config_set("notify-keyspace-events", "Ex")

    return {'id': request.session.session_id}
