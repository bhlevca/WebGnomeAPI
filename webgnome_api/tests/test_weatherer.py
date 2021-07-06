"""
Functional tests for the Gnome Environment object Web API
These include (Wind, Tide, etc.)
"""
from datetime import datetime, timedelta

from .base import FunctionalTestBase


class BaseWeathererTests(FunctionalTestBase):
    '''
        Tests out the Gnome Wind object API
    '''
    req_data = {'obj_type': 'gnome.weatherers.Evaporation',
                'active_range': ('-inf', 'inf'),
                'on': True,
                }

    def test_get_no_id(self):
        resp = self.testapp.get('/weatherer')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.items()]

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

        for k in ('id', 'obj_type', 'active_range', 'on'):
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
        self.now = datetime.now()
        self.active_range = (self.now.isoformat(),
                             (self.now + timedelta(60 * 60 * 24)).isoformat())

        print(self.active_range)

        json_obj['active_range'] = self.active_range
        json_obj['on'] = False

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj['active_range'] == list(self.active_range)
        assert json_obj['on'] is False


class BurnTests(BaseWeathererTests):
    '''
    cleanup operations must have a valid datetime - cannot use -inf
    Burn ignores active_stop if it is given since burn will stop when thickness
    is 2mm
    '''
    req_data = {'obj_type': 'gnome.weatherers.Burn',
                'json_': 'webapi',
                'active_range': ('2014-04-09T15:00:00', 'inf'),
                'on': True,
                'area': 10,
                'area_units': 'm^2',
                'thickness': 1,
                'thickness_units': 'm'
                }

    def check_updates(self, json_obj):
        '''
            The Burn object accepts an active range, but only utilizes the
            start time.  The stop time is calculated internally by the object.
        '''
        assert json_obj['active_range'][0] == self.active_range[0]
        assert json_obj['on'] is False


class ROCBurnTests(BaseWeathererTests):

    req_data = {'obj_type': 'gnome.weatherers.roc.Burn',
                'json_': 'webapi',
                'on': True,
                'offset': '50',
                'boom_length': '250',
                'boom_draft': '10',
                'speed': '2',
                'throughput': '0.75',
                'burn_efficiency_type': '1',
                'timeseries': [["2016-12-29T07:00:00", "2016-12-29T19:00:00"],
                               ["2016-12-30T07:00:00", "2016-12-30T19:00:00"]
                               ],
                'units': {'offset': 'ft',
                          'boom_length': 'ft',
                          'boom_draft': 'in',
                          'speed': 'knots'
                          }
                }


class SkimmerTests(BaseWeathererTests):
    '''
    cleanup operations must have a valid datetime - cannot use -inf and inf
    active_range is used to get the mass removal rate
    '''
    req_data = {'obj_type': 'gnome.weatherers.Skimmer',
                'json_': 'webapi',
                'active_range': ('2014-04-09T15:00:00', '2014-04-09T19:00:00'),
                'on': True,
                'amount': 100,
                'units': 'm^3',
                'efficiency': .3
                }

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        self.now = datetime.now()

        json_obj['active_range'] = (self.now.isoformat(),
                                    (self.now + timedelta(days=1))
                                    .isoformat())
        json_obj['on'] = False

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        assert json_obj['active_range'] == [self.now.isoformat(),
                                            (self.now + timedelta(days=1))
                                            .isoformat()]
        assert json_obj['on'] is False

    def test_put_with_low_active_stop(self):
        '''
            Similar to test_put_valid_id, but we want to test updating
            active_range with a range that is outside and
            below the current active range.
        '''
        self.now = datetime.now()
        req_data = self.req_data

        req_data['active_range'] = ((self.now + timedelta(days=3))
                                    .isoformat(),
                                    (self.now + timedelta(days=4))
                                    .isoformat())

        resp = self.testapp.post_json('/weatherer', params=req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/weatherer', params=req_data)
        self.check_updates(resp.json_body)


class ChemicalDispersionTests(BaseWeathererTests):
    '''
        Mock objects at present so just test that they get created
    '''
    req_data = {'obj_type': 'gnome.weatherers.ChemicalDispersion',
                'json_': 'webapi',
                'active_range': ('-inf', 'inf'),
                'on': True,
                'fraction_sprayed': 0.2,
                'efficiency': 1.0,
                }


class BeachingTests(BaseWeathererTests):
    '''
        Mock objects at present so just test that they get created
    '''
    req_data = {'obj_type': 'gnome.weatherers.manual_beaching.Beaching',
                'active_range': ('-inf', 'inf'),
                'on': True,
                'name': 'Beaching',
                'units': 'm^3',
                'timeseries': [('2015-04-27T10:00:00', 16),
                               ('2015-04-27T16:00:00', 17),
                               ('2015-04-27T22:00:00', 19),
                               ('2015-04-28T04:00:00', 15)]
                }

    def perform_updates(self, json_obj):
        '''
            Note: When setting active range, we need to remember that the
                  Beaching object will internally force the stop time
                  equal to the last datetime in the timeseries.
                  This will happen as the timeseries property is set.
        '''
        self.now = datetime(2015, 4, 27)

        json_obj['active_range'] = (self.now.isoformat(),
                                    (self.now + timedelta(days=1))
                                    .isoformat())
        json_obj['on'] = False

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        end_range = datetime.strptime(self.req_data['timeseries'][-1][0],
                                      '%Y-%m-%dT%H:%M:%S')
        assert json_obj['active_range'] == [self.now.isoformat(),
                                            end_range.isoformat()]
        assert json_obj['on'] is False

    def test_put_empty_timeseries(self):
        resp = self.testapp.post_json('/weatherer', params=self.req_data)
        beaching = resp.json_body

        assert isinstance(beaching['timeseries'], list)
        assert len(beaching['timeseries']) > 0
        beaching['timeseries'] = []

        resp = self.testapp.put_json('/weatherer', params=beaching)
        beaching = resp.json_body

        assert beaching['timeseries'] == []
