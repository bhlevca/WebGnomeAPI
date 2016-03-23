"""
Functional tests for the Gnome Outputter object Web API
"""
from base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class OutputterTests(FunctionalTestBase):
    '''
        Tests out the Gnome Outputter object API
    '''
    req_data = {'obj_type': u'gnome.outputters.outputter.Outputter',
                'name': u'Outputter',
                'output_timestep': 1800.0,
                'output_last_step': True,
                'output_zero_step': True,
                }

    def test_get_no_id(self):
        resp = self.testapp.get('/outputter')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/outputter/{0}'.format(obj_id), status=404)

    def test_post_no_payload(self):
        self.testapp.post_json('/outputter', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/outputter', status=400)

    def test_put_no_id(self):
        self.testapp.put_json('/outputter', params=self.req_data, status=404)

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/outputter', params=params, status=404)

    def test_get_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. perform an additional get of the object with a valid id
        # 4. check that our new JSON response matches the one from the create
        resp1 = self.testapp.post_json('/outputter', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/outputter/{0}'.format(obj_id))

        self.check_created_values(resp1.json_body, resp2.json_body)

    def test_put_valid_id(self):
        resp = self.testapp.post_json('/outputter', params=self.req_data)
        outputter = resp.json_body

        self.perform_updates(outputter)
        print 'Response:'
        pp.pprint(resp.json_body)
        resp = self.testapp.put_json('/outputter', params=outputter)
        print 'Response:'
        pp.pprint(resp.json_body)

        self.check_updates(resp.json_body)

    def check_created_values(self, json_obj1, json_obj2):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        for k in ('name', 'output_timestep',
                  'output_last_step', 'output_zero_step'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        json_obj['output_timestep'] = 1200.0
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj['output_timestep'] == 1200.0
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False


class RendererTests(OutputterTests):
    '''
        Tests out the Gnome Renderer object API
    '''
    req_data = {'obj_type': 'gnome.outputters.renderer.Renderer',
                'name': 'Renderer',
                'output_last_step': True,
                'output_zero_step': True,
                'draw_ontop': 'forecast',
                'map_filename': 'models/Test.bna',
                'output_dir': 'models/images',
                'image_size': [800, 600],
                'viewport': [[-71.2242987892, 42.1846263908],
                             [-70.4146871963, 42.6329573908]]
                }

    def check_created_values(self, json_obj1, json_obj2):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        for k in ('name',
                  'output_last_step', 'output_zero_step',
                  'draw_ontop', 'map_filename', 'output_dir',
                  'image_size', 'viewport'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False
        json_obj['draw_ontop'] = 'uncertain'
        json_obj['viewport'] = [[-100.0, 100.0],
                                [-100.0, 100.0]]

    def check_updates(self, json_obj):
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False
        assert json_obj['draw_ontop'] == 'uncertain'

        assert json_obj['viewport'] == [[-100.0, 100.0],
                                        [-100.0, 100.0]]


class NetCDFOutputterTests(OutputterTests):
    '''
        Tests out the Gnome NetCDFOutput object API
    '''
    req_data = {'obj_type': u'gnome.outputters.netcdf.NetCDFOutput',
                'name': u'sample_model.nc',
                'netcdf_filename': u'sample_model.nc',
                'compress': True,
                'output_last_step': True,
                'output_zero_step': True}

    def check_created_values(self, json_obj1, json_obj2):
        for k in ('name', 'netcdf_filename',
                  'compress', 'output_last_step', 'output_zero_step'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False
        json_obj['compress'] = False

    def check_updates(self, json_obj):
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False
        assert json_obj['compress'] is False


class GeoJsonOutputterTests(OutputterTests):
    '''
        Tests out the Gnome GeoJson object API
    '''
    req_data = {'obj_type': u'gnome.outputters.TrajectoryGeoJsonOutput',
                'name': u'GeoJson',
                'output_last_step': True,
                'output_zero_step': True}

    def check_created_values(self, json_obj1, json_obj2):
        for k in ('name', 'output_last_step', 'output_zero_step'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False

    def check_updates(self, json_obj):
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False


class CurrentOutputterTests(OutputterTests):
    '''
        Tests out the Gnome GeoJson object API
    '''
    req_data = {'obj_type': u'gnome.outputters.CurrentGeoJsonOutput',
                'name': u'CurrentGrid',
                'output_last_step': True,
                'output_zero_step': True,
                'current_movers': [{'obj_type': u'gnome.movers.CatsMover',
                                    'filename': 'models/tidesWAC.CUR',
                                    'scale': True,
                                    'scale_value': 1.0,
                                    'tide': {'obj_type': 'gnome.environment.Tide',
                                             'filename': 'models/CLISShio.txt',
                                             },
                                    }]
                }

    def check_created_values(self, json_obj1, json_obj2):
        for k in ('name', 'output_last_step', 'output_zero_step'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False

    def check_updates(self, json_obj):
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False


class IceGeoJsonOutputterTests(OutputterTests):
    '''
        Tests out the Gnome GeoJson object API
    '''
    req_data = {'obj_type': u'gnome.outputters.IceGeoJsonOutput',
                'name': u'IceGeoJsonOutput',
                'on': True,
                'output_last_step': True,
                'output_zero_step': True,
                'ice_movers': [{'obj_type': u'gnome.movers.IceMover',
                                'name': u'IceMover',
                                'active_start': '-inf',
                                'active_stop': 'inf',
                                'on': True,
                                'current_scale': 1.0,
                                'filename': u'models/acnfs_example.nc',
                                'topology_file': u'models/acnfs_topo.dat',
                                'uncertain_along': 0.5,
                                'uncertain_cross': 0.25,
                                'uncertain_duration': 24.0,
                                'uncertain_time_delay': 0.0
                                }]
                }

    def check_created_values(self, json_obj1, json_obj2):
        for k in ('name', 'output_last_step', 'output_zero_step'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False

    def check_updates(self, json_obj):
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False


class IceImageOutputterTests(IceGeoJsonOutputterTests):
    '''
        Tests out the Gnome GeoJson object API
    '''
    def setUp(self):
        super(IceImageOutputterTests, self).setUp()
        self.req_data['obj_type'] = u'gnome.outputters.IceImageOutput'

    def check_created_values(self, json_obj1, json_obj2):
        for k in ('name', 'output_last_step', 'output_zero_step'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False

    def check_updates(self, json_obj):
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False


class IceRawJsonOutputterTests(IceGeoJsonOutputterTests):
    '''
        Tests out the Gnome Raw Json Ice Outputter object API
    '''
    def setUp(self):
        super(IceRawJsonOutputterTests, self).setUp()
        self.req_data['obj_type'] = u'gnome.outputters.IceRawJsonOutput'

    def check_created_values(self, json_obj1, json_obj2):
        for k in ('name', 'output_last_step', 'output_zero_step'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False

    def check_updates(self, json_obj):
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False


class WeatheringOutputterTests(OutputterTests):
    '''
        Tests out the Gnome GeoJson object API
    '''
    req_data = {'obj_type': u'gnome.outputters.weathering.WeatheringOutput',
                'name': u'WeatheringOutput',
                'output_last_step': True,
                'output_zero_step': True}

    def check_created_values(self, json_obj1, json_obj2):
        for k in ('name', 'output_last_step', 'output_zero_step'):
            assert json_obj1[k] == json_obj2[k]

    def perform_updates(self, json_obj):
        json_obj['output_last_step'] = False
        json_obj['output_zero_step'] = False

    def check_updates(self, json_obj):
        assert json_obj['output_last_step'] is False
        assert json_obj['output_zero_step'] is False
