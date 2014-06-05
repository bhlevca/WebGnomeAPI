"""
Functional tests for the Gnome Location object Web API
"""
from base import FunctionalTestBase


class LocationTestBase(FunctionalTestBase):
    '''
        Tests out the Gnome Location object API
    '''
    def test_get_no_id(self):
        resp = self.testapp.get('/location')

        print 'resp:\n', resp
        raise
