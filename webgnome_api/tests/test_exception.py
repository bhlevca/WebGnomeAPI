"""
Functional tests for the Gnome Environment object Web API
These include (Wind, Tide, etc.)
"""
import ujson

from .base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)


class ExceptionTests(FunctionalTestBase):
    '''
        Tests out the Gnome Exception handling API
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
                'units': 'meter per second'
                }

    def test_post(self):
        req_data = self.req_data.copy()
        req_data['units'] = 'bogus'
        resp = self.testapp.post_json('/environment', params=req_data,
                                      expect_errors=True)
        print('status:', (resp.status_code,))
        error_resp = resp.json_body

        print('json_body:')
        pp.pprint(error_resp)

        assert resp.status_code == 415
        assert error_resp['exc_type'] == 'InvalidUnitError'

    def test_put(self):
        resp = self.testapp.post_json('/environment', params=self.req_data)

        obj_id = resp.json_body['id']
        req_data = resp.json_body
        req_data['units'] = 'bogus'

        resp = self.testapp.put_json('/environment/{0}'.format(obj_id),
                                     params=req_data,
                                     expect_errors=True)
        print('status:', (resp.status_code,))
        error_resp = resp.json_body

        print('json_body:')
        pp.pprint(error_resp)

        assert resp.status_code == 415
        assert error_resp['exc_type'] == 'InvalidUnitError'


class ModelExceptionTests(FunctionalTestBase):
    '''
        Tests out the Gnome Exception handling API
    '''
    req_data = {'obj_type': 'gnome.model.Model',
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

    def test_post_with_nested_environment(self):
        req_data = self.req_data.copy()
        req_data['environment'] = [{'obj_type': 'gnome.environment.Wind',
                                    'description': 'Wind Object',
                                    'updated_at': '2014-03-26T14:52:45.385126',
                                    'source_type': 'undefined',
                                    'source_id': 'undefined',
                                    'timeseries': [('2012-11-06T20:10:30',
                                                    (1.0, 0.0)),
                                                   ('2012-11-06T20:15:30',
                                                    (1.0, 270.0))],
                                    'units': 'bogus'
                                    }]

        resp = self.testapp.post_json('/model', params=req_data,
                                      expect_errors=True)
        print('status:', (resp.status_code,))
        error_resp = resp.json_body

        print('json_body:')
        pp.pprint(error_resp)

        assert resp.status_code == 415
        assert error_resp['exc_type'] == 'InvalidUnitError'

    def test_put_with_nested_environment(self):
        req_data = self.req_data.copy()
        req_data['environment'] = [{'obj_type': 'gnome.environment.Wind',
                                    'description': 'Wind Object',
                                    'updated_at': '2014-03-26T14:52:45.385126',
                                    'source_type': 'undefined',
                                    'source_id': 'undefined',
                                    'timeseries': [('2012-11-06T20:10:30',
                                                    (1.0, 0.0)),
                                                   ('2012-11-06T20:15:30',
                                                    (1.0, 270.0))],
                                    'units': 'meter per second'
                                    }]

        resp = self.testapp.post_json('/model', params=req_data)
        model1 = resp.json_body

        model1['environment'][0]['units'] = 'bogus'

        resp = self.testapp.put_json('/model', params=model1,
                                     expect_errors=True)
        print('status:', (resp.status_code,))
        print(('json_body: {}'.format(resp.json_body)))
        error_resp = resp.json_body

        print('json_body:')
        pp.pprint(error_resp)

        assert resp.status_code == 415
        assert error_resp['exc_type'] == 'InvalidUnitError'


class StepExceptionTest(FunctionalTestBase):
    '''
        Tests out the exceptions in the step api
    '''
    def test_step_no_active_model(self):
        # the step api should fail with no active model initialized.
        resp = self.testapp.get('/step', expect_errors=True)
        status_code = resp.status_code
        explanation = resp.body.encode('utf-8').split('\n')[2]

        assert status_code == 412
        assert (explanation ==
                'Your session timed out - the model is no longer active')
