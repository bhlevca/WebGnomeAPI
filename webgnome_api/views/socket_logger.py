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
        self.emit("you_just_connected", {'bravo': 'kid'})
        self.spawn(self.cpu_checker_process)

    def recv_json(self, data):
        self.emit("got_some_json", data)

    def on_bob(self, *args):
        self.broadcast_event('broadcasted', args)
        self.socket['/chat'].emit('bob')

    def cpu_checker_process(self):
        """This will be a greenlet"""
        ret = os.system("cat /proc/cpu/stuff")
        self.emit("cpu_value", ret)


class ChatIONamespace(BaseNamespace, RoomsMixin):
    def on_mymessage(self, msg):
        print "In on_mymessage"
        self.send("little message back")
        self.send({'blah': 'blah'}, json=True)
        for x in xrange(2):
            self.emit("pack", {'the': 'more', 'you': 'can'})

    def on_my_callback(self, packet):
        return (1, 2)

    def on_trigger_server_callback(self, superbob):
        def cb():
            print "OK, WE WERE CALLED BACK BY THE ACK! THANKS :)"
        self.emit('callmeback', 'this is a first param',
                  'this is the last param', callback=cb)

        def cb2(param1, param2):
            print "OK, GOT THOSE VALUES BACK BY CB", param1, param2
        self.emit('callmeback', 'this is a first param',
                  'this is the last param', callback=cb2)

    def on_rtc_invite(self, sdp):
        print "Got an RTC invite, now pushing to others..."
        self.emit_to_room('room1', 'rtc_invite', self.session['nickname'],
                          sdp)

    def recv_connect(self):
        self.session['nickname'] = 'guest123'
        self.join('room1')

    def recv_message(self, data):
        print "Received a 'message' with data:", data

    def on_disconnect_me(self, data):
        print "Disconnecting you buddy", data
        self.disconnect()


nsmap = {'': GlobalIONamespace,
         '/logger': ChatIONamespace}


@view_config(route_name='logger')
def socketio_service(request):
    """ The view that will launch the socketio listener """

    pp.pprint(request.environ)
    socketio_manage(request.environ, namespaces=nsmap, request=request)

    return {}
