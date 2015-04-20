from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

import os

from pyramid.view import view_config

import gevent
from gevent import socket

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin


class GlobalIONamespace(BaseNamespace, BroadcastMixin):
    def on_chat(self, *args):
        self.emit("bob", {'hello': 'world'})
        print "Received chat message", args
        self.broadcast_event_not_me('chat', *args)

    def recv_connect(self):
        print "CONNNNNNNN"
        self.emit("you_just_connected",
                  {'bravo': 'kid'}
                  )

    def recv_json(self, data):
        self.emit("got_some_json", data)

    def on_bob(self, *args):
        self.broadcast_event('broadcasted', args)
        self.socket['/chat'].emit('bob')


nsmap = {'/logger': GlobalIONamespace,
         }


@view_config(route_name='socket.io')
def socketio_service(request):
    """ The view that will launch the socketio listener """

    socketio_manage(request.environ, namespaces=nsmap, request=request)

    return {}
