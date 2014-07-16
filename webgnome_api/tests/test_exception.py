"""
Functional tests for the Gnome Environment object Web API
These include (Wind, Tide, etc.)
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)
import json

from base import FunctionalTestBase


class ExceptionTests(FunctionalTestBase):
    '''
        Tests out the Gnome Exception handling API
    '''
    req_data = {'obj_type': 'gnome.environment.Wind',
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

    def test_post(self):
        req_data = self.req_data.copy()
        req_data['units'] = 'bogus'
        resp = self.testapp.post_json('/environment', params=req_data,
                                      expect_errors=True)
        print 'status:', (resp.status_code,)
        error_resp = json.loads(resp.json_body)

        print 'json_body:'
        pp.pprint(error_resp)

        assert resp.status_code == 415
        assert error_resp[-1][:16] == 'InvalidUnitError'

    def test_put(self):
        resp = self.testapp.post_json('/environment', params=self.req_data)

        obj_id = resp.json_body['id']
        req_data = resp.json_body
        req_data['units'] = 'bogus'

        resp = self.testapp.put_json('/environment/{0}'.format(obj_id),
                                     params=req_data,
                                     expect_errors=True)
        print 'status:', (resp.status_code,)
        error_resp = json.loads(resp.json_body)

        print 'json_body:'
        pp.pprint(error_resp)

        assert resp.status_code == 415
        assert error_resp[-1][:16] == 'InvalidUnitError'
        raise