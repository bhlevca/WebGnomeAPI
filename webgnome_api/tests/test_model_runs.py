"""
Functional tests for the Gnome Location object Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

import os
import time

import pytest

from base import FunctionalTestBase


class ModelRunTest(FunctionalTestBase):
    '''
        Tests out a Model run with the WebGnome API
    '''
    spill_data = {'obj_type': 'gnome.spill.spill.Spill',
                  'name': 'What a Name',
                  'on': True,
                  'release': {'obj_type': ('gnome.spill.release'
                                           '.PointLineRelease'),
                              'num_elements': 1000,
                              'num_released': 0,
                              'release_time': '2014-08-06T08:00:00',
                              'end_release_time': '2014-08-06T08:00:00',
                              'start_time_invalid': False,
                              'end_position': [-72.419992, 41.202120, 0.0],
                              'start_position': [-72.419992, 41.202120, 0.0]
                              },
                  'element_type': {'obj_type': ('gnome.spill.elements'
                                                '.ElementType'),
                                   'initializers': [{'obj_type': 'gnome.spill.elements.InitWindages',
                                                     'windage_range': [0.01, 0.04],
                                                     'windage_persist': 900,
                                                     },
                                                    {'obj_type': 'gnome.spill.elements.InitMassFromSpillAmount'},
                                                    {'obj_type': 'gnome.spill.elements.InitArraysFromOilProps'}
                                                    ],
                                   'substance': u'ALAMO'
                                   },
                  'amount': 200,
                  'units': 'tons'
                  }
    renderer_data = {'obj_type': 'gnome.outputters.renderer.Renderer',
                     'name': 'Renderer',
                     'output_last_step': True,
                     'output_zero_step': True,
                     'draw_ontop': 'forecast',
                     'filename': 'models/Test.bna',
                     'images_dir': 'models/images',
                     'image_size': [800, 600],
                     'viewport': [[-71.2242987892, 42.1846263908],
                                  [-70.4146871963, 42.6329573908]]
                     }
    geojson_data = {'obj_type': 'gnome.outputters.geo_json.GeoJson',
                    'name': 'GeoJson',
                    'output_last_step': True,
                    'output_zero_step': True,
                    }
    evaporate_data = {'obj_type': 'gnome.weatherers.Evaporation',
                      'name': 'Evaporation',
                      'wind': {'obj_type': 'gnome.environment.Wind',
                               'name': 'ConstantWind',
                               'timeseries': [('2012-11-06T20:10:30',
                                               (1.0, 0.0))],
                               'units': u'meter per second'},
                      'water': {'obj_type': 'gnome.environment.Water',
                                'temperature': 46,
                                'salinity': 32,
                                'sediment': 5,
                                'wave_height': 0,
                                'fetch': 0,
                                'units': {'temperature': 'F',
                                          'salinity': 'psu',
                                          'sediment': 'mg/l',
                                          'wave_height': 'm',
                                          'fetch': 'm',
                                          'density': 'kg/m^3',
                                          'kinematic_viscosity': 'm^2/s'
                                          }
                                }
                      }

    @pytest.mark.slow
    @pytest.mark.parametrize()
    def test_full_run(self):
        # We are testing our ability to generate the first step in a model run
        resp = self.testapp.get('/location/central-long-island-sound')

        assert 'name' in resp.json_body
        assert 'steps' in resp.json_body
        assert 'geometry' in resp.json_body
        assert 'coordinates' in resp.json_body['geometry']

        # OK, if we get this far, we should have an active model
        print 'test_all_steps(): getting model...'
        resp = self.testapp.get('/model')
        model1 = resp.json_body
        model1['start_time'] = self.spill_data['release']['release_time']
        num_time_steps = model1['num_time_steps']

        print 'Our model:'
        pp.pprint(model1)
        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # so what do we still need?
        # - maybe a wind and a windmover??? (optional)

        #print 'our map:'
        #pp.pprint(model1['map'])
        #raise

        # - we need a spill
        print 'test_all_steps(): creating spill...'
        resp = self.testapp.post_json('/spill', params=self.spill_data)
        spill = resp.json_body
        model1['spills'] = [spill]

        # add evaporation weatherer
        resp = self.testapp.post_json('/weatherer', params=self.evaporate_data)
        evaporate = resp.json_body
        model1['weatherers'] = [evaporate]

        # - we need an outputter
        print 'test_all_steps(): creating outputter...'

        resp = self.testapp.post_json('/outputter', params=self.geojson_data)
        outputter = resp.json_body
        model1['outputters'] = [outputter]

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert model1['spills'][0]['id'] == spill['id']
        assert model1['outputters'][0]['id'] == outputter['id']

        # Alright, now we can try to cycle through our steps.
        print 'num_steps = ', num_time_steps

        for s in range(num_time_steps):
            resp = self.testapp.get('/step')
            step = resp.json_body
            print '{0}, '.format(step['GeoJson']['step_num']),
            assert step['GeoJson']['step_num'] == s
            assert 'feature_collection' in step['GeoJson']

        # an additional call to /step should generate a 404
        resp = self.testapp.get('/step', status=404)

        time.sleep(4)
        print 'done!'
