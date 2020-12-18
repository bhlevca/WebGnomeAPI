
from pyramid.view import view_config

#from socketio import socketio_manage
#from socketio.namespace import BaseNamespace
socketio_manage = 1
BaseNamespace = object
from webgnome_api.views.socket_logger import LoggerNamespace
from webgnome_api.views.socket_step import StepNamespace
from pyramid.response import Response


@view_config(route_name='socket.io')
def socketio_service(request):
    """ The view that will launch the socketio listener """
    resp = socketio_manage(request.environ,
                           namespaces={'/socket': WSNamespace,
                                       '/logger': LoggerNamespace,
                                       '/step_socket': StepNamespace,
                                       },
                           request=request)
    print('socketio_manage() returned:', resp)
    #return resp
    return Response()


class WSNamespace(BaseNamespace):

    def on_echo(self, echo, *args, **kwargs):
        self.emit(echo, *args, **kwargs)

    def on_getsession(self):
        print(self.session)

    def recv_connect(self):
        print("CONN WS")
