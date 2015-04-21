from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

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
            while True:
                for line in Pygtail('webgnome_api.log'):
                    self.emit('log',
                              {'session_id': self.request.session.session_id,
                               'message': line}
                              )
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
