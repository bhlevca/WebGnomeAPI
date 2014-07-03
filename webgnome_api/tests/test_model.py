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
                'weatherers': [],
                'outputters': [],
                'spills': [],
                }

    def test_post_with_nested_map(self):
        req_data = self.req_data.copy()
        req_data['map'] = {'obj_type': 'gnome.map.MapFromBNA',
                           'filename': 'models/Test.bna',
                           'refloat_halflife': 1.0
                           }

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        assert 'filename' in model1['map']
        assert 'refloat_halflife' in model1['map']

    def test_put_with_nested_map(self):
        req_data = self.req_data.copy()
        req_data['map'] = {'obj_type': 'gnome.map.MapFromBNA',
                           'filename': 'models/Test.bna',
                           'refloat_halflife': 1.0
                           }

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        model1['map']['refloat_halflife'] = 2.0

        resp = self.testapp.post_json('/model', params=model1)
        model2 = resp.json_body

        assert model2['map']['refloat_halflife'] == 2.0

    def test_post_with_nested_environment(self):
        req_data = self.req_data.copy()
        req_data['environment'] = [{'obj_type': 'gnome.environment.Wind',
                                    'description': u'Wind Object',
                                    'updated_at': '2014-03-26T14:52:45.385126',
                                    'source_type': u'undefined',
                                    'source_id': u'undefined',
                                    'timeseries': [('2012-11-06T20:10:30',
                                                    (1.0, 0.0)),
                                                   ('2012-11-06T20:15:30',
                                                    (1.0, 270.0))],
                                    'units': u'meter per second'
                                    }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        print 'Response:'
        pp.pprint(model1)

        assert 'environment' in model1
        assert model1['environment'][0]['obj_type'] == 'gnome.environment.wind.Wind'
        assert 'description' in model1['environment'][0]
        assert 'timeseries' in model1['environment'][0]
        assert 'units' in model1['environment'][0]

    def test_put_with_nested_environment(self):
        req_data = self.req_data.copy()
        req_data['environment'] = [{'obj_type': 'gnome.environment.Wind',
                                    'description': u'Wind Object',
                                    'updated_at': '2014-03-26T14:52:45.385126',
                                    'source_type': u'undefined',
                                    'source_id': u'undefined',
                                    'timeseries': [('2012-11-06T20:10:30',
                                                    (1.0, 0.0)),
                                                   ('2012-11-06T20:15:30',
                                                    (1.0, 270.0))],
                                    'units': u'meter per second'
                                    }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        model1['environment'][0]['units'] = 'knots'

        resp = self.testapp.post_json('/model', params=model1)
        model2 = resp.json_body

        assert model2['environment'][0]['units'] == 'knots'

    def test_post_with_nested_mover(self):
        req_data = self.req_data.copy()
        req_data['movers'] = [{'obj_type': 'gnome.movers.wind_movers.WindMover',
                               'active_start': '-inf',
                               'active_stop': 'inf',
                               'on': True,
                               'uncertain_angle_scale': 0.4,
                               'uncertain_duration': 3.0,
                               'uncertain_speed_scale': 2.0,
                               'uncertain_time_delay': 0.0,
                               'wind': {'obj_type': 'gnome.environment.Wind',
                                        'description': u'Wind Object',
                                        'updated_at': '2014-03-26T14:52:45.385126',
                                        'source_type': u'undefined',
                                        'source_id': u'undefined',
                                        'units': u'meter per second',
                                        'timeseries': [('2012-11-06T20:10:30',
                                                        (1.0, 0.0)),
                                                       ('2012-11-06T20:11:30',
                                                        (1.0, 45.0)),
                                                       ('2012-11-06T20:12:30',
                                                        (1.0, 90.0)),
                                                       ('2012-11-06T20:13:30',
                                                        (1.0, 120.0)),
                                                       ('2012-11-06T20:14:30',
                                                        (1.0, 180.0)),
                                                       ('2012-11-06T20:15:30',
                                                        (1.0, 270.0))],
                                        }
                               }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        print 'Response:'
        pp.pprint(model1)

        assert 'movers' in model1
        assert model1['movers'][0]['obj_type'] == 'gnome.movers.wind_movers.WindMover'
        assert 'active_start' in model1['movers'][0]
        assert 'active_stop' in model1['movers'][0]
        assert 'on' in model1['movers'][0]
        assert 'uncertain_angle_scale' in model1['movers'][0]
        assert 'uncertain_duration' in model1['movers'][0]
        assert 'uncertain_speed_scale' in model1['movers'][0]
        assert 'uncertain_time_delay' in model1['movers'][0]
        assert 'description' in model1['movers'][0]['wind']
        assert 'updated_at' in model1['movers'][0]['wind']
        assert 'source_type' in model1['movers'][0]['wind']
        assert 'source_id' in model1['movers'][0]['wind']
        assert 'timeseries' in model1['movers'][0]['wind']
        assert 'units' in model1['movers'][0]['wind']

    def test_put_with_nested_mover(self):
        req_data = self.req_data.copy()
        req_data['movers'] = [{'obj_type': 'gnome.movers.wind_movers.WindMover',
                               'active_start': '-inf',
                               'active_stop': 'inf',
                               'on': True,
                               'uncertain_angle_scale': 0.4,
                               'uncertain_duration': 3.0,
                               'uncertain_speed_scale': 2.0,
                               'uncertain_time_delay': 0.0,
                               'wind': {'obj_type': 'gnome.environment.Wind',
                                        'description': u'Wind Object',
                                        'updated_at': '2014-03-26T14:52:45.385126',
                                        'source_type': u'undefined',
                                        'source_id': u'undefined',
                                        'units': u'meter per second',
                                        'timeseries': [('2012-11-06T20:10:30',
                                                        (1.0, 0.0)),
                                                       ('2012-11-06T20:11:30',
                                                        (1.0, 45.0)),
                                                       ('2012-11-06T20:12:30',
                                                        (1.0, 90.0)),
                                                       ('2012-11-06T20:13:30',
                                                        (1.0, 120.0)),
                                                       ('2012-11-06T20:14:30',
                                                        (1.0, 180.0)),
                                                       ('2012-11-06T20:15:30',
                                                        (1.0, 270.0))],
                                        }
                               }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        model1['movers'][0]['wind']['units'] = 'knots'

        resp = self.testapp.post_json('/model', params=model1)
        model2 = resp.json_body

        assert model2['movers'][0]['wind']['units'] == 'knots'

    def test_post_with_nested_weatherer(self):
        req_data = self.req_data.copy()
        req_data['weatherers'] = [{'obj_type': u'gnome.weatherers.core.Weatherer',
                                   'active_start': '-inf',
                                   'active_stop': 'inf',
                                   'on': True,
                                   }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        print 'Response:'
        pp.pprint(model1)

        assert 'weatherers' in model1
        assert model1['weatherers'][0]['obj_type'] == 'gnome.weatherers.core.Weatherer'
        assert 'active_start' in model1['weatherers'][0]
        assert 'active_stop' in model1['weatherers'][0]
        assert 'on' in model1['weatherers'][0]

    def test_put_with_nested_weatherer(self):
        req_data = self.req_data.copy()
        req_data['weatherers'] = [{'obj_type': u'gnome.weatherers.core.Weatherer',
                                   'active_start': '-inf',
                                   'active_stop': 'inf',
                                   'on': True,
                                   }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        model1['weatherers'][0]['on'] = False

        resp = self.testapp.post_json('/model', params=model1)
        model2 = resp.json_body

        assert model2['weatherers'][0]['on'] == False

    def test_post_with_nested_outputter(self):
        '''
            TODO: Apparently, this works as a nested object of the model,
                  But we don't have the standalone outputter methods yet.
                  We need to do that.
        '''
        req_data = self.req_data.copy()
        req_data['outputters'] = [{'obj_type': 'gnome.outputters.renderer.Renderer',
                                   'name': 'Renderer',
                                   'output_last_step': True,
                                   'output_zero_step': True,
                                   'draw_ontop': 'forecast',
                                   'filename': ('models/Test.bna'),
                                   'images_dir': ('models/images'),
                                   'image_size': [800, 600],
                                   'viewport': [[-71.2242987892, 42.1846263908],
                                                [-70.4146871963, 42.6329573908]]
                                   }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        print 'Response:'
        pp.pprint(model1)

        assert 'outputters' in model1
        assert model1['outputters'][0]['obj_type'] == 'gnome.outputters.renderer.Renderer'
        assert 'name' in model1['outputters'][0]
        assert 'output_last_step' in model1['outputters'][0]
        assert 'output_zero_step' in model1['outputters'][0]
        assert 'draw_ontop' in model1['outputters'][0]
        assert 'filename' in model1['outputters'][0]
        assert 'images_dir' in model1['outputters'][0]
        assert 'image_size' in model1['outputters'][0]
        assert 'viewport' in model1['outputters'][0]

    def test_put_with_nested_outputter(self):
        '''
            TODO: Apparently, this works as a nested object of the model,
                  But we don't have the standalone outputter methods yet.
                  We need to do that.
        '''
        req_data = self.req_data.copy()
        req_data['outputters'] = [{'obj_type': 'gnome.outputters.renderer.Renderer',
                                   'name': 'Renderer',
                                   'output_last_step': True,
                                   'output_zero_step': True,
                                   'draw_ontop': 'forecast',
                                   'filename': ('models/Test.bna'),
                                   'images_dir': ('models/images'),
                                   'image_size': [800, 600],
                                   'viewport': [[-71.2242987892, 42.1846263908],
                                                [-70.4146871963, 42.6329573908]]
                                   }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        print 'Response:'
        pp.pprint(model1)
        model1['outputters'][0]['output_last_step'] = False

        resp = self.testapp.post_json('/model', params=model1)
        model2 = resp.json_body

        assert model2['outputters'][0]['output_last_step'] == False
