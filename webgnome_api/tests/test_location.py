"""
Functional tests for the Gnome Location object Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from base import FunctionalTestBase


class LocationTest(FunctionalTestBase):
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
        assert 'steps' in resp.json_body
        assert 'geometry' in resp.json_body
        assert 'coordinates' in resp.json_body['geometry']

        # OK, if we get this far, we should have an active model
        resp = self.testapp.get('/model')
        model1 = resp.json_body

        # the location file we selected should have a registered map
        map_id = model1['map']['id']
        print 'GET: /map/{0}'.format(map_id)
        resp = self.testapp.get('/map/{0}'.format(map_id))
        map1 = resp.json_body
        assert map1['id'] == model1['map']['id']

        # the location file we selected should have a registered Tide
        env_id = model1['environment'][0]['id']
        print 'GET: /environment/{0}'.format(env_id)
        resp = self.testapp.get('/environment/{0}'.format(env_id))
        env1 = resp.json_body
        assert env1['id'] == model1['environment'][0]['id']

        # the location file we selected should have a registered RandomMover
        mover1_id = model1['movers'][0]['id']
        print 'GET: /mover/{0}'.format(mover1_id)
        resp = self.testapp.get('/mover/{0}'.format(mover1_id))
        mover1 = resp.json_body
        assert mover1['id'] == model1['movers'][0]['id']

        # the location file we selected should have a registered CatsMover
        mover2_id = model1['movers'][1]['id']
        print 'GET: /mover/{0}'.format(mover2_id)
        resp = self.testapp.get('/mover/{0}'.format(mover2_id))
        mover2 = resp.json_body
        assert mover2['id'] == model1['movers'][1]['id']
