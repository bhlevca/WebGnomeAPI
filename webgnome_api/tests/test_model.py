"""
Functional tests for the Model Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from base import FunctionalTestBase


class ModelTests(FunctionalTestBase):
    req_data = {'obj_type': u'gnome.model.Model',
                'cache_enabled': False,
                'duration': 86400.0,
                'start_time': '2014-04-09T15:00:00',
                'time_step': 900.0,
                'uncertain': False,
                'weathering_substeps': 1,
                'environment': [],
                'movers': [],
                'outputters': [],
                'spills': [],
                'weatherers': [],
                }

    def test_get_model_no_id(self):
        resp = self.testapp.get('/model')

        #pp.pprint(resp.json_body)
        assert 'id' in resp.json_body
        assert 'start_time' in resp.json_body
        assert 'time_step' in resp.json_body
        assert 'duration' in resp.json_body
        assert 'cache_enabled' in resp.json_body
        assert 'environment' in resp.json_body
        assert 'spills' in resp.json_body
        assert 'movers' in resp.json_body
        assert 'weatherers' in resp.json_body
        assert 'map_id' in resp.json_body
        assert 'uncertain' in resp.json_body
        # what other kinds of validation should we have here?

    def test_get_model_no_id_active(self):
        '''
            Here we test the get with no ID, but where an active model
            is attached to the session.
        '''
        resp = self.testapp.get('/model')
        model1 = resp.json_body

        resp = self.testapp.get('/model')
        model2 = resp.json_body

        assert model1['id'] == model2['id']

    def test_get_model_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/model/{0}'.format(obj_id), status=404)

    def test_get_model_invalid_id_active(self):
        '''
            Here we test the get with an invalid ID, but where an active model
            is attached to the session.
        '''
        resp = self.testapp.get('/model')
        model1 = resp.json_body

        obj_id = 0xdeadbeef
        self.testapp.get('/model/{0}'.format(obj_id), status=404)

    def test_get_model_valid_id(self):
        resp = self.testapp.get('/model')
        model1 = resp.json_body

        resp = self.testapp.get('/model/{0}'.format(model1['id']))
        model2 = resp.json_body

        assert model1['id'] == model2['id']

    def test_post_no_payload(self):
        self.testapp.post_json('/model', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/model', status=400)

    def test_put_model_no_id(self):
        if False:
            print '\n\nModel Put Request payload: {0}'.format(self.req_data)
            resp = self.testapp.put_json('/model', params=self.req_data)
            print '\nModel Put Response payload: {0}'.format(resp.json_body)
        else:
            print 'Not Implemented'

        # TODO: This should be working, but we need to put some asserts
        #       in here to validate what we are getting
