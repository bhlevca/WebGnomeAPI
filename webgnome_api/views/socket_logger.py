import re
import base64
import hashlib

from pygtail import Pygtail

from pyramid.view import view_config

import gevent
from gevent import socket

from socketio import socketio_manage
from socketio.namespace import BaseNamespace


class LoggerNamespace(BaseNamespace):
    def recv_connect(self):
        print "CONNNNNNNN"
        self.emit("you_just_connected",
                  {'bravo': 'kid'}
                  )

        def send_logs():
            hasher = hashlib.sha1(self.request.session.session_id)
            session_hash = base64.urlsafe_b64encode(hasher.digest())
            pattern = re.compile('^(?P<date>.*?)\s+'
                                 '(?P<time>.*?)\s+'
                                 '(?P<level>.*?)\s+'
                                 '(?P<session_hash>.*?)\s+'
                                 '(?P<name>.*?)\s+'
                                 '(?P<message>.*?)$')

            while True:
                for line in Pygtail('webgnome_api.log'):
                    if line.find(session_hash) >= 0:
                        msg_obj = pattern.match(line).groupdict()
                        del msg_obj['session_hash']

                        self.emit('log', msg_obj)

                gevent.sleep(0.1)
        self.spawn(send_logs)


@view_config(route_name='socket.io')
def socketio_service(request):
    """ The view that will launch the socketio listener """

    resp = socketio_manage(request.environ,
                           namespaces={'/logger': LoggerNamespace,
                                       },
                           request=request)
    print 'socketio_manage() returned:', resp
    return resp
