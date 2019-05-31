import re
import base64
import hashlib

from pygtail import Pygtail

import gevent

from socketio.namespace import BaseNamespace
import logging
import os
import pdb

class LoggerNamespace(BaseNamespace):

    def __init__(self, *args, **kwargs):
        super(LoggerNamespace, self).__init__(*args, **kwargs)
        self.sess_id = self.request.session.session_id
        self.sess_hash = self.request.session_hash

    def recv_connect(self):
        print "CONN LOGGER " + self.sess_hash
        self.emit("connected")

        overall_logger = logging.root
        formatter = overall_logger.handlers[0].formatter
        pattern = re.compile('^(?P<date>.*?)\s+'
                             '(?P<time>.*?)\s+'
                             '(?P<level>.*?)\s+'
                             '(?P<session_hash>.*?)\s+'
                             '(?P<name>.*?)\s+'
                             '(?P<message>.*?)$')

        overall_logger.info('{0} handlers attached'.format(len(overall_logger.handlers)))
        overall_logger.info('{0}'.format(self.socket))
        if len(overall_logger.handlers) > 50:
            #To stop the logger root from getting drowned in handlers
            del overall_logger.handlers[2];

        existing_handler=None
        for i, handler in enumerate(overall_logger.handlers):
            if (hasattr(handler, 'session_id') and handler.session_id == self.sess_id):
                overall_logger.info('existing handler for the session {0} found'.format(self.sess_id))
                existing_handler = overall_logger.handlers[i]

        def gen_emit_msg(sess_hash):
            def emit_msg(logrecord):
                if hasattr(logrecord, 'session_hash') and logrecord.session_hash == self.sess_hash:
                    msg_obj = pattern.match(formatter.format(logrecord)).groupdict()
                    del msg_obj['session_hash']
                    self.emit('log', msg_obj)
                    return True
                else:
                    return False
            return emit_msg

        if existing_handler is None:
            session_filter = logging.Filter()
            session_filter.filter = gen_emit_msg(self.sess_hash)

            session_log_folder = os.path.join(os.getcwd(), 'models', 'session', self.sess_id)
            session_log_file = os.path.join(session_log_folder, self.sess_id + '.log')
            session_handler = logging.handlers.RotatingFileHandler(session_log_file,
                                                                   mode='a',
                                                                   maxBytes=1000000,
                                                                   backupCount=3,
                                                                   encoding=None,
                                                                   delay=0)
            session_handler.formatter = formatter
            session_handler.session_id = self.sess_id
            overall_logger.info('handler for session {0} added'.format(self.sess_id))
            session_handler.addFilter(session_filter)

            overall_logger.addHandler(session_handler)
        else:
            existing_handler.filters[0].filter = gen_emit_msg(self.sess_hash)

    def on_start_logger(self):
        print "Starting logger greenlet"
        self.emit("logger_started")
