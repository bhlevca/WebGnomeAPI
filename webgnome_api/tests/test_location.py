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

    def test_get_invalid_id(self):
        self.testapp.get('/location/bogus', status=404)

    def test_get_valid_id(self):
        resp = self.testapp.get('/location/central-long-island-sound')

        assert 'name' in resp.json_body
        assert 'coords' in resp.json_body
        assert 'steps' in resp.json_body
