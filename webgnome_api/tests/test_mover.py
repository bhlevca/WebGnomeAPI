"""
Functional tests for the Mover Web API
"""
from base import FunctionalTestBase


class BaseMoverTests(FunctionalTestBase):
    '''
        Tests out the Gnome Mover common APIs
    '''
    req_data = {'obj_type': 'gnome.movers.simple_mover.SimpleMover',
                'uncertainty_scale': 0.5,
                'velocity': (1.0, 1.0, 1.0)
                }

    def test_get_no_id(self):
        resp = self.testapp.get('/mover')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/mover/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. perform an additional get of the object with a valid id
        # 4. check that our new JSON response matches the one from the create
        resp1 = self.testapp.post_json('/mover', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/mover/{0}'.format(obj_id))

        for a in ('id', 'obj_type', 'active_start', 'active_stop'):
            assert resp2.json_body[a] == resp1.json_body[a]

    def test_post_no_payload(self):
        self.testapp.post_json('/mover', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/mover', status=400)

    def test_put_no_id(self):
        self.testapp.put_json('/mover', params=self.req_data, status=404)

    def check_create_properties(self, response):
        for k in ('id', 'obj_type', 'on', 'active_start', 'active_stop'):
            assert k in response.json_body


class SimpleMoverTests(BaseMoverTests):
    '''
        Tests out the Gnome Simple Mover API
    '''
    req_data = {'obj_type': 'gnome.movers.simple_mover.SimpleMover',
                'active_start': '-inf',
                'active_stop': 'inf',
                'on': True,
                'uncertainty_scale': 0.5,
                'velocity': (1.0, 1.0, 1.0)
                }

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/mover', params=params, status=404)

    def test_put_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. update the properties in the JSON response
        # 4. update the object by performing a put with a valid id
        # 5. check that our new properties are in the new JSON response
        resp = self.testapp.post_json('/mover', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/mover', params=req_data)
        self.check_updates(resp.json_body)

    def check_create_properties(self, response):
        super(SimpleMoverTests, self).check_create_properties(response)

        # specific to SimpleMover()
        assert 'velocity' in response.json_body

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        json_obj['velocity'] = [10.0, 10.0, 10.0]
        json_obj['on'] = False

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj[u'velocity'] == [10.0, 10.0, 10.0]
        assert json_obj['on'] is False


class WindMoverTests(BaseMoverTests):
    '''
        Tests out the Gnome Wind Mover API
    '''
    wind_req_data = {'obj_type': 'gnome.environment.Wind',
                     'description': u'Wind Object',
                     'updated_at': '2014-03-26T14:52:45.385126',
                     'source_type': u'undefined',
                     'source_id': u'undefined',
                     'timeseries': [('2012-11-06T20:10:30', (1.0, 0.0)),
                                    ('2012-11-06T20:11:30', (1.0, 45.0)),
                                    ('2012-11-06T20:12:30', (1.0, 90.0)),
                                    ('2012-11-06T20:13:30', (1.0, 120.0)),
                                    ('2012-11-06T20:14:30', (1.0, 180.0)),
                                    ('2012-11-06T20:15:30', (1.0, 270.0))],
                     'units': u'meter per second'
                     }

    req_data = {'obj_type': 'gnome.movers.wind_movers.WindMover',
                'active_start': '-inf',
                'active_stop': 'inf',
                'on': True,
                'uncertain_angle_scale': 0.4,
                'uncertain_angle_units': u'rad',
                'uncertain_duration': 3.0,
                'uncertain_speed_scale': 2.0,
                'uncertain_time_delay': 0.0,
                'wind': None
                }

    def test_get_valid_id(self):
        # 1. create a Wind object
        # 2. create a WindMover object
        # 3. get the WindMover valid id for use in the URL
        # 4. perform an additional get of the object with a valid id
        # 5. check that our new JSON response matches the one from the create
        wind_obj = self.create_wind_obj(self.wind_req_data)
        self.req_data['wind'] = wind_obj

        resp1 = self.testapp.post_json('/mover', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/mover/{0}'.format(obj_id))

        for a in ('id', 'obj_type', 'active_start', 'active_stop'):
            assert resp2.json_body[a] == resp1.json_body[a]

        for a in ('uncertain_angle_scale',
                  'uncertain_duration',
                  'uncertain_speed_scale',
                  'uncertain_time_delay'):
            assert resp2.json_body[a] == resp1.json_body[a]

    def test_put_no_id(self):
        # WindMover reauires a valid Wind object for creation
        wind_obj = self.create_wind_obj(self.wind_req_data)
        self.req_data['wind'] = wind_obj

        self.testapp.put_json('/mover', params=self.req_data, status=404)

    def test_put_invalid_id(self):
        # WindMover reauires a valid Wind object for creation
        wind_obj = self.create_wind_obj(self.wind_req_data)
        self.req_data['wind'] = wind_obj

        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/mover', params=params, status=404)

    def test_put_valid_id(self):
        # 1. create a Wind object
        # 2. create a WindMover object
        # 3. get the WindMover valid id for use in the URL
        # 3. update the properties in the JSON response
        # 4. update the object by performing a put with a valid id
        # 5. check that our new properties are in the new JSON response

        # WindMover reauires a valid Wind object for creation
        wind_obj = self.create_wind_obj(self.wind_req_data)
        self.req_data['wind'] = wind_obj

        resp = self.testapp.post_json('/mover', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/mover', params=req_data)
        self.check_updates(resp.json_body)

    def create_wind_obj(self, req_data):
        resp = self.testapp.post_json('/environment', params=req_data)
        return resp.json_body

    def check_create_properties(self, response):
        super(WindMoverTests, self).check_create_properties(response)

        # specific to WindMover()
        assert 'uncertain_angle_scale' in response.json_body
        assert 'uncertain_angle_units' in response.json_body
        assert 'uncertain_duration' in response.json_body
        assert 'uncertain_speed_scale' in response.json_body
        assert 'uncertain_time_delay' in response.json_body
        assert 'wind' in response.json_body

    def perform_updates(self, json_obj):
        json_obj['uncertain_duration'] = 2.0
        json_obj['uncertain_speed_scale'] = 3.0
        json_obj['uncertain_time_delay'] = 4.0

    def check_updates(self, json_obj):
        assert json_obj['uncertain_duration'] == 2.0
        assert json_obj['uncertain_speed_scale'] == 3.0
        assert json_obj['uncertain_time_delay'] == 4.0


class RandomMoverTests(BaseMoverTests):
    '''
        Tests out the Gnome Random Mover API
    '''
    req_data = {'obj_type': u'gnome.movers.random_movers.RandomMover',
                'name': u'RandomMover',
                'active_start': '-inf',
                'active_stop': 'inf',
                'on': True,
                'diffusion_coef': 100000.0,
                'uncertain_factor': 2.0
                }

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/mover', params=params, status=404)

    def test_put_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. update the properties in the JSON response
        # 4. update the object by performing a put with a valid id
        # 5. check that our new properties are in the new JSON response
        resp = self.testapp.post_json('/mover', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/mover', params=req_data)
        self.check_updates(resp.json_body)

    def check_create_properties(self, response):
        super(SimpleMoverTests, self).check_create_properties(response)

        # specific to SimpleMover()
        assert 'velocity' in response.json_body

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        json_obj['diffusion_coef'] = 20000.0
        json_obj['on'] = False

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj['diffusion_coef'] == 20000.0
        assert json_obj['on'] is False


class RandomVerticalMoverTests(BaseMoverTests):
    '''
        Tests out the Gnome Random Vertical Mover API
    '''
    req_data = {'obj_type': u'gnome.movers.random_movers.RandomVerticalMover',
                'name': u'RandomVerticalMover',
                'active_start': '-inf',
                'active_stop': 'inf',
                'on': True,
                'mixed_layer_depth': 10.0,
                'vertical_diffusion_coef_above_ml': 5.0,
                'vertical_diffusion_coef_below_ml': 0.11
                }

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/mover', params=params, status=404)

    def test_put_valid_id(self):
        resp = self.testapp.post_json('/mover', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/mover', params=req_data)
        self.check_updates(resp.json_body)

        model_id = resp.json_body['id']
        resp = self.testapp.get('/mover/{0}'.format(model_id))
        self.check_updates(resp.json_body)

    def check_create_properties(self, response):
        super(RandomVerticalMoverTests, self).check_create_properties(response)

        # specific to SimpleMover()
        assert 'velocity' in response.json_body

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        json_obj['mixed_layer_depth'] = 20.0
        json_obj['vertical_diffusion_coef_above_ml'] = 10.0
        json_obj['vertical_diffusion_coef_below_ml'] = 0.22

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj['mixed_layer_depth'] == 20.0
        assert json_obj['vertical_diffusion_coef_above_ml'] == 10.0
        assert json_obj['vertical_diffusion_coef_below_ml'] == 0.22


class CatsMoverTests(BaseMoverTests):
    '''
        Tests out the Gnome Cats Mover API
        - Kinda needs a Tide object
    '''
    tide_data = {'obj_type': 'gnome.environment.Tide',
                 'filename': 'models/CLISShio.txt',
                 }

    req_data = {'obj_type': u'gnome.movers.current_movers.CatsMover',
                'filename': 'models/tidesWAC.CUR',
                'scale': True,
                'scale_value': 1.0,
                }

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/mover', params=params, status=404)

    def test_put_valid_id(self):
        req_data = {}
        req_data.update(self.req_data)

        resp = self.testapp.post_json('/environment', params=self.tide_data)
        tide = resp.json_body
        req_data['tide'] = tide

        resp = self.testapp.post_json('/mover', params=req_data)
        mover = resp.json_body

        self.perform_updates(mover)

        resp = self.testapp.put_json('/mover', params=mover)
        self.check_updates(resp.json_body)

        model_id = resp.json_body['id']
        resp = self.testapp.get('/mover/{0}'.format(model_id))
        self.check_updates(resp.json_body)

    def check_create_properties(self, response):
        super(RandomVerticalMoverTests, self).check_create_properties(response)

        # specific to SimpleMover()
        assert 'velocity' in response.json_body

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        json_obj['scale'] = False
        json_obj['scale_value'] = 2.0
        json_obj['scale_refpoint'] = [-50.0, 50.0, 10.0]

        json_obj['up_cur_uncertain'] = 0.5
        json_obj['down_cur_uncertain'] = -0.5
        json_obj['left_cur_uncertain'] = -0.5
        json_obj['right_cur_uncertain'] = 0.5

        json_obj['uncertain_duration'] = 60.0
        json_obj['uncertain_eddy_diffusion'] = 1.0
        # json_obj['uncertain_eddy_v0'] = 1.0  # failing
        json_obj['uncertain_time_delay'] = 1.0

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj['scale'] is False
        assert json_obj['scale_value'] == 2.0
        assert json_obj['scale_refpoint'] == [-50.0, 50.0, 10.0]

        assert json_obj['up_cur_uncertain'] == 0.5
        assert json_obj['down_cur_uncertain'] == -0.5
        assert json_obj['left_cur_uncertain'] == -0.5
        assert json_obj['right_cur_uncertain'] == 0.5

        assert json_obj['uncertain_duration'] == 60.0
        assert json_obj['uncertain_eddy_diffusion'] == 1.0
        assert json_obj['uncertain_time_delay'] == 1.0


class AggregateCurrentInfoTests(FunctionalTestBase):
    '''
        Tests out the API for getting the aggregate current info
        from all movers in the model.
    '''
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
    req_data['movers'] = [{'obj_type': u'gnome.movers.CatsMover',
                           'filename': 'models/tidesWAC.CUR',
                           'scale': True,
                           'scale_value': 1.0,
                           'tide': {'obj_type': 'gnome.environment.Tide',
                                    'filename': 'models/CLISShio.txt',
                                    },
                           }]

    def test_get_incomplete_paths(self):
        params = {}
        params.update(self.req_data)

        # step 1: we create a model that contains a current mover.
        resp = self.testapp.post_json('/model', params=params)
        model = resp.json_body

        assert model['movers'][0]['tide']['filename'] == 'CLISShio.txt'

        # step 2: we perform some gets that have incomplete urls
        self.testapp.get('/mover/{0}'.format('current'), status=404)
        self.testapp.get('/mover/{0}/'.format('current'), status=404)
        self.testapp.get('/mover/{0}/{1}'.format('current', 'bogus'),
                         status=404)
        self.testapp.get('/mover/{0}/{1}/'.format('current', 'bogus'),
                         status=404)

    def test_get_complete_path(self):
        '''
            We are not done here, but this is about as far as we can go
            for now.
        '''
        params = {}
        params.update(self.req_data)

        # step 1: we create a model that contains a current mover.
        resp = self.testapp.post_json('/model', params=params)
        model = resp.json_body

        assert model['movers'][0]['tide']['filename'] == 'CLISShio.txt'

        # step 2: we perform some gets that have complete urls
        resp = self.testapp.get('/mover/{0}/{1}'.format('current', 'grid'))
        current_info = resp.json_body
        assert 'features' in current_info
        assert 'type' in current_info
        assert current_info['type'] == 'FeatureCollection'

        features = current_info['features']
        for f in features:
            assert 'type' in f
            assert f['type'] == 'Feature'

            assert 'geometry' in f
            geo = f['geometry']
            assert 'coordinates' in geo
            assert 'type' in geo
            assert geo['type'] == 'MultiPolygon'

        resp = self.testapp.get('/mover/{0}/{1}/'.format('current', 'grid'))
        current_info = resp.json_body
        assert 'features' in current_info
        assert 'type' in current_info
        assert current_info['type'] == 'FeatureCollection'

        features = current_info['features']
        for f in features:
            assert 'type' in f
            assert f['type'] == 'Feature'

            assert 'geometry' in f
            geo = f['geometry']
            assert 'coordinates' in geo
            assert 'type' in geo
            assert geo['type'] == 'MultiPolygon'
