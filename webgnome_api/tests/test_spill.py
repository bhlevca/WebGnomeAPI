"""
Functional tests for the Gnome Spill object Web API
"""
from base import FunctionalTestBase


class SpillTests(FunctionalTestBase):
    '''
        Tests out the Gnome Spill object API
    '''
    rel_req_data = {
                    'obj_type': u'gnome.spill.release.PointLineRelease',
                    'json_': u'webapi',
                    'num_elements': 100,
                    'num_released': 0,
                    'release_time': '2014-04-15T13:22:20.930570',
                    'start_time_invalid': True,
                    'end_release_time': '2014-04-15T13:22:20.930570',
                    'end_position': (28.0, -78.0, 0.0),
                    'start_position': (28.0, -78.0, 0.0),
                    }

    req_data = {'obj_type': u'gnome.spill.spill.Spill',
                }

    def create_release_obj(self, req_data):
        resp = self.testapp.put_json('/release', params=req_data)
        return resp.json_body

    def test_get_no_id(self):
        resp = self.testapp.get('/spill')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/spill/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create a Release object
        # 2. create a Spill object
        # 3. get the valid id from the Spill response
        # 4. perform an additional get of the object with a valid id
        # 5. check that our new JSON response matches the one from the create
        rel_obj = self.create_release_obj(self.rel_req_data)
        self.req_data['wind'] = rel_obj

        resp1 = self.testapp.put_json('/spill', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/spill/{0}'.format(obj_id))

        for a in ('id', 'obj_type', 'on'):
            assert resp2.json_body[a] == resp1.json_body[a]

        assert resp2.json_body['id'] == obj_id
        assert resp2.json_body['obj_type'] == resp1.json_body['obj_type']

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        json_obj['num_elements'] = 100
        json_obj['num_released'] = 50
        json_obj['start_time_invalid'] = False

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj['num_elements'] == 100
        assert json_obj['num_released'] == 50
        assert json_obj['start_time_invalid'] == False
