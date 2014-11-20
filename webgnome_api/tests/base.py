"""
base.py: Base classes for different types of tests.
"""
import os
import shutil
from unittest import TestCase

from pyramid import testing
from paste.deploy.loadwsgi import appconfig
from webtest import TestApp

from gnome.multi_model_broadcast import ModelBroadcaster
from webgnome_api import main


class GnomeTestCase(TestCase):
    def setUp(self):
        here = os.path.dirname(__file__)
        self.project_root = os.path.abspath(os.path.dirname(here))

    def get_settings(self, config_file='../../webgnome_api.ini#webgnome_api'):
        here = os.path.dirname(__file__)
        return appconfig('config:%s' % config_file, relative_to=here)


class FunctionalTestBase(GnomeTestCase):
    def setUp(self):
        super(FunctionalTestBase, self).setUp()

        self.settings = self.get_settings()
        app = main(None, **self.settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        'Clean up any images the model generated after running tests.'
        print '>> FunctionalTestBase.tearDown()...'
        test_images_dir = os.path.join(self.project_root, 'static', 'img',
                                       self.settings['model_data_dir'])
        shutil.rmtree(test_images_dir, ignore_errors=True)

        self.cleanup_web_app_upon_shutdown()

    def cleanup_web_app_upon_shutdown(self):
        '''
            Every test case gets a new instantiated web application,
            and there are some resources that our web application manages
            that need to be cleaned up before the next one gets created.

            It would be nice if pyramid would provide a cleanup method
            upon shutdown.
        '''
        app = self.testapp.app

        for session_values in app.registry.settings['objects'].values():
            for v in session_values.values():
                if isinstance(v, ModelBroadcaster):
                    v.stop()

        if hasattr(app.registry, '_redis_sessions'):
            app.registry._redis_sessions.connection_pool.disconnect()


class UnitTestBase(GnomeTestCase):
    def setUp(self):
        super(UnitTestBase, self).setUp()

        self.config = testing.setUp()
        self.settings = self.get_settings()

    def tearDown(self):
        testing.tearDown()

    def get_request(self, *args, **kwargs):
        return testing.DummyRequest(*args, **kwargs)

    def get_resource(self, *args, **kwargs):
        return testing.DummyResource(*args, **kwargs)
