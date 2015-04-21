from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from threading import Timer
from pygtail import Pygtail

from pyramid.view import view_config

import gevent
from gevent import socket

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin


class GlobalIONamespace(BaseNamespace, BroadcastMixin):
    def recv_connect(self):
        print "CONNNNNNNN"
        self.emit("you_just_connected",
                  {'bravo': 'kid'}
                  )
        self.tail_file = Pygtail('webgnome_api.log')

        self.timer = Timer(1, self.on_timer)
        self.timer.start()

    def recv_json(self, data):
        self.emit("got_some_json", data)

    def on_timer(self):
        print 'on_timer called back...'
        for line in self.tail_file:
            self.send(line)


nsmap = {'/logger': GlobalIONamespace,
         }


@view_config(route_name='socket.io')
def socketio_service(request):
    """ The view that will launch the socketio listener """

    socketio_manage(request.environ, namespaces=nsmap, request=request)

