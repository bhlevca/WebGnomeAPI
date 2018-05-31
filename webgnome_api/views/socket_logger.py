import re
import base64
import hashlib

from pygtail import Pygtail

import gevent

from socketio.namespace import BaseNamespace


class LoggerNamespace(BaseNamespace):
    def recv_connect(self):
        print "CONN LOGGER"
        self.emit("connected")

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
                for line in Pygtail('messages.log'):
                    if line.find(session_hash) >= 0:
                        msg_obj = pattern.match(line).groupdict()
                        del msg_obj['session_hash']

                        self.emit('log', msg_obj)

                gevent.sleep(0.1)

        self.spawn(send_logs)

    def on_start_logger(self):
        print "Starting logger greenlet"
        self.emit("logger_started")
