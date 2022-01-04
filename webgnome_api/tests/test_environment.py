"""
Functional tests for the Gnome Environment object Web API
These include (Wind, Tide, etc.)
"""

from pathlib import Path

from .base import FunctionalTestBase, MODELS_DIR


class WindTests(FunctionalTestBase):
    '''
        Tests out the Gnome Wind object API
    '''
    req_data = {'obj_type': 'gnome.environment.Wind',
                'description': 'Wind Object',
                'updated_at': '2014-03-26T14:52:45.385126',
                'source_type': 'undefined',
                'source_id': 'undefined',
                'timeseries': [('2012-11-06T20:10:30', (1.0, 0.0)),
                               ('2012-11-06T20:11:30', (1.0, 45.0)),
                               ('2012-11-06T20:12:30', (1.0, 90.0)),
                               ('2012-11-06T20:13:30', (1.0, 120.0)),
                               ('2012-11-06T20:14:30', (1.0, 180.0)),
                               ('2012-11-06T20:15:30', (1.0, 270.0))],
                'units': 'meter per second',
                'latitude': 90,
                'longitude': 90,
                }

    def test_get_no_id(self):
        resp = self.testapp.get('/environment')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.items()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/environment/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. perform an additional get of the object with a valid id
        # 4. check that our new JSON response matches the one from the create
        resp1 = self.testapp.post_json('/environment', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/environment/{0}'.format(obj_id))

        for k in ('id', 'obj_type'):
            assert resp2.json_body[k] == resp1.json_body[k]

    def test_post_no_payload(self):
        self.testapp.post_json('/environment', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/environment', status=400)

    def test_put_no_id(self):
        self.testapp.put_json('/environment', params=self.req_data, status=404)

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/environment', params=params, status=404)

    def test_put_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. update the properties in the JSON response
        # 4. update the object by performing a put with a valid id
        # 5. check that our new properties are in the new JSON response
        resp = self.testapp.post_json('/environment', params=self.req_data)

        obj_id = resp.json_body['id']
        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/environment/{0}'.format(obj_id),
                                     params=req_data)
        self.check_updates(resp.json_body)

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        json_obj['description'] = 'Wind Object (updated)'

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert 'id' in json_obj
        assert 'obj_type' in json_obj
        assert 'description' in json_obj
        assert json_obj['description'] == 'Wind Object (updated)'


class TideTests(WindTests):
    '''
        Tests out the Gnome Tide object API
    '''
    req_data = {'obj_type': 'gnome.environment.Tide',
                'filename': str(MODELS_DIR / 'CLISShio.txt'),
                }

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
            Currently, it does not make sense to update any Tide object
            attributes.
        '''
        pass

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
            Currently, it does not make sense to update any Tide object
            attributes.
        '''
        pass


class WaterTests(WindTests):
    '''
        Tests out the Gnome Water API - just include tests in base class for
        now
    '''
    req_data = {'obj_type': 'gnome.environment.Water',
                'temperature': 46,
                'salinity': 32,
                'sediment': 5,
                'wave_height': 0,
                'fetch': 0,
                'units': {
                    'temperature': 'F',
                    'salinity': 'psu',
                    'sediment': 'mg/l',
                    'wave_height': 'm',
                    'fetch': 'm',
                    'density': 'kg/m^3',
                    'kinematic_viscosity': 'm^2/s'
                    }
                }

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
            Currently, it does not make sense to update any Tide object
            attributes.
        '''
        pass

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
            Currently, it does not make sense to update any Tide object
            attributes.
        '''
        pass
