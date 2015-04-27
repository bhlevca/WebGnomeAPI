'''
    Middleware Classes for handling py_gnome functionality
    These will be processes that can massage an incoming request
    so that it will be more easily digestible to py_gnome.
    This will make it so the Web Client doesn't have to work quite as hard.
'''
import base64
import hashlib

import json

from webgnome_api.common.common_object import ValueIsJsonObject


class PyGnomeSchemaTweenFactory(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

        # one-time configuration code goes here

    def add_json_key(self, json_request):
        modified = False

        if ValueIsJsonObject(json_request):
            if 'json_' not in json_request:
                json_request['json_'] = 'webapi'
                modified = True

        if isinstance(json_request, dict):
            for v in json_request.values():
                if self.add_json_key(v):
                    modified = True
        elif isinstance(json_request, (list, tuple)):
            for v in json_request:
                if self.add_json_key(v):
                    modified = True

        return modified

    def generate_short_session_id(self, request):
        if hasattr(request, 'session'):
            hasher = hashlib.sha1(request.session.session_id)
            request.session_hash = base64.urlsafe_b64encode(hasher.digest())

    def before_the_handler(self, request):
        # code to be executed for each request
        # BEFORE the actual application code
        # goes here
        if ('CONTENT_TYPE' in request.environ and
                request.environ['CONTENT_TYPE'][:16] == 'application/json' and
                request.body):
            json_request = json.loads(request.body)

            if self.add_json_key(json_request):
                # TODO: The tween seems like a logical place to do
                #       Preprocessing on a request.
                #       But it seems like a wasteful use of processing
                #       to evaluate our JSON request, update some content,
                #       and then turn it back into a string.
                #       I tried just leaving it as a JSON object, but the
                #       request body doesn't accept anything but a string.
                request.body = json.dumps(json_request)

        self.generate_short_session_id(request)

    def after_the_handler(self, response):
        # code to be executed for each request
        # AFTER the actual application code
        # goes here
        pass

    def __call__(self, request):
        self.before_the_handler(request)

        response = self.handler(request)

        self.after_the_handler(response)

        return response
