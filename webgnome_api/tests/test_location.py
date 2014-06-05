"""
Functional tests for the Gnome Location object Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from base import FunctionalTestBase


class LocationTestBase(FunctionalTestBase):
    '''
        Tests out the Gnome Location object API
    '''
    def test_get_no_id(self):
        resp = self.testapp.get('/location')

        print 'resp:'
        pp.pprint(resp.json_body)
        assert 'type' in resp.json_body
        assert 'features' in resp.json_body
        for f in resp.json_body['features']:
            assert 'type' in f
            assert 'properties' in f
            assert 'geometry' in f

            assert 'title' in f['properties']
            assert 'slug' in f['properties']
            assert 'content' in f['properties']

            assert 'type' in f['geometry']
            assert 'coordinates' in f['geometry']
