import socketio

class WebgnomeSocketioServer(socketio.Server):
    def __init__(self,
                 app_settings=None,
                 **kwargs):
        self.app_settings = app_settings
        super(socketio.Server, self).__init__(**kwargs)

