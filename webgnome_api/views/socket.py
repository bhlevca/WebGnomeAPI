
from pyramid.view import view_config
from pyramid.response import Response

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from webgnome_api.views.socket_logger import LoggerNamespace
from webgnome_api.views.socket_step import StepNamespace
from ..common.views import cors_response


@view_config(route_name='socket.io')
def socketio_service(request):
    """ The view that will launch the socketio listener """
    resp = socketio_manage(request.environ,
                           namespaces={'/socket': WSNamespace,
                                       '/logger': LoggerNamespace,
                                       '/step_socket': StepNamespace,
                                       },
                           request=request)
    resp = Response()
    print 'socketio_manage() returned:', resp
    return resp


class WSNamespace(BaseNamespace):

    def on_echo(self, echo, *args, **kwargs):
        self.emit(echo, *args, **kwargs)

    def on_getsession(self):
        print self.session

    def recv_connect(self):
        print "CONN WS"
