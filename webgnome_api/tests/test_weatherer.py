"""
Functional tests for the Gnome Environment object Web API
These include (Wind, Tide, etc.)
"""
from datetime import datetime

from base import FunctionalTestBase


class BaseWeathererTests(FunctionalTestBase):
    '''
        Tests out the Gnome Wind object API
    '''
    req_data = {'obj_type': u'gnome.weatherers.Evaporation',
                'active_start': '-inf',
                'active_stop': 'inf',
                'on': True,
                }

    def test_get_no_id(self):
        resp = self.testapp.get('/weatherer')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/weatherer/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. perform an additional get of the object with a valid id
        # 4. check that our new JSON response matches the one from the create
        resp1 = self.testapp.post_json('/weatherer', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/weatherer/{0}'.format(obj_id))

        for k in ('id', 'obj_type', 'active_start', 'on'):
            assert resp2.json_body[k] == resp1.json_body[k]

    def test_post_no_payload(self):
        self.testapp.post_json('/weatherer', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/weatherer', status=400)

    def test_put_no_id(self):
        self.testapp.put_json('/weatherer', params=self.req_data, status=404)

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/weatherer', params=params, status=404)

    def test_put_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. update the properties in the JSON response
        # 4. update the object by performing a put with a valid id
        # 5. check that our new properties are in the new JSON response
        resp = self.testapp.post_json('/weatherer', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/weatherer', params=req_data)
        self.check_updates(resp.json_body)

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        self.now = datetime.now().isoformat()
        json_obj['active_start'] = self.now
        json_obj['on'] = False

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj['active_start'] == self.now
        assert json_obj['on'] is False


class BurnTests(BaseWeathererTests):
    '''
    cleanup operations must have a valid datetime - cannot use -inf
    Burn ignores active_stop if it is given since burn will stop when thickness
    is 2mm
    '''
    req_data = {'obj_type': u'gnome.weatherers.Burn',
                'json_': 'webapi',
                'active_start': '2014-04-09T15:00:00',
                'on': True,
                'area': 10,
                'area_units': 'm^2',
                'thickness': 1,
                'thickness_units': 'm'
                }


class SkimmerTests(BaseWeathererTests):
    '''
    cleanup operations must have a valid datetime - cannot use -inf and inf
    active_start/active_stop is used to get the mass removal rate
    '''
    req_data = {'obj_type': u'gnome.weatherers.Skimmer',
                'json_': 'webapi',
                'active_start': '2014-04-09T15:00:00',
                'active_stop': '2014-04-09T19:00:00',
                'on': True,
                'amount': 100,
                'units': 'm^3',
                'efficiency': .3
                }


class DispersionTests(BaseWeathererTests):
    '''
        Mock objects at present so just test that they get created
    '''
    req_data = {'obj_type': u'gnome.weatherers.Dispersion',
                'json_': 'webapi',
                'active_start': '-inf',
                'active_stop': 'inf',
                'on': True,
                }
