"""
Functional tests for the Model Web API
"""
import time
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
        specs = resp.json_body

        assert 'id' in specs['Model']
        for k in ('id', 'start_time', 'time_step', 'duration',
                  'cache_enabled', 'uncertain', 'map',
                  'environment', 'spills', 'movers', 'weatherers'):
            assert k in specs['Model']
        # what other kinds of validation should we have here?

    def test_get_model_no_id_active(self):
        '''
            Here we test the get with no ID, but where an active model
            is attached to the session.
        '''
        resp = self.testapp.post_json('/model')
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
        resp = self.testapp.post_json('/model')
        model1 = resp.json_body

        resp = self.testapp.get('/model/{0}'.format(model1['id']))
        model2 = resp.json_body

        assert model1['id'] == model2['id']

    def test_post_no_payload(self):
        '''
            This case is different than the other object create methods.
            We would like to be able to post with no payload and receive
            a newly created 'blank' Model.
        '''
        resp = self.testapp.post_json('/model')
        model1 = resp.json_body

        for k in ('id', 'start_time', 'time_step', 'duration',
                  'cache_enabled', 'uncertain', 'map',
                  'environment', 'spills', 'movers', 'weatherers'):
            assert k in model1

    def test_post_no_payload_twice(self):
        resp = self.testapp.post_json('/model')
        model1 = resp.json_body

        resp = self.testapp.post_json('/model')
        model2 = resp.json_body

        assert model1['id'] != model2['id']

    def test_post_with_payload_no_map(self):
        resp = self.testapp.post_json('/model', params=self.req_data)
        model1 = resp.json_body

    def test_post_with_payload_none_map(self):
        req_data = self.req_data.copy()
        req_data['map'] = None

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

    def test_put_no_payload(self):
        self.testapp.put_json('/model', status=400)

    def test_put_no_id_no_active_model(self):
        resp = self.testapp.put_json('/model', params=self.req_data,
                                     status=404)

    def test_put_no_id_active_model(self):
        resp = self.testapp.post_json('/model', params=self.req_data)

        model1 = resp.json_body
        model1['time_step'] = 1800.0

        resp = self.testapp.put_json('/model', params=model1)
        model2 = resp.json_body

        assert model2['time_step'] == 1800.0

    def test_put_valid_id(self):
        resp = self.testapp.post_json('/model', params=self.req_data)

        model1 = resp.json_body
        model1['time_step'] = 1800.0

        resp = self.testapp.put_json('/model', params=model1)

        model2 = resp.json_body
        assert model2['time_step'] == 1800.0


class NestedModelTests(FunctionalTestBase):
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

    def test_post_with_payload_nested_map(self):
        req_data = self.req_data.copy()
        req_data['map'] = {'obj_type': 'gnome.map.MapFromBNA',
                           'filename': 'models/Test.bna',
                           'refloat_halflife': 1.0
                           }

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

