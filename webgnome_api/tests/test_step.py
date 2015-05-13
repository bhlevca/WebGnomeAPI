"""
Functional tests for the Gnome Location object Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

import pytest

from base import FunctionalTestBase


class StepTest(FunctionalTestBase):
    '''
        Tests out the Gnome Location object API
    '''
    spill_data = {'obj_type': 'gnome.spill.spill.Spill',
                  'name': 'What a Name',
                  'on': True,
                  'release': {'obj_type': ('gnome.spill.release'
                                           '.PointLineRelease'),
                              'num_elements': 1000,
                              'num_released': 84,
                              'release_time': '2013-02-13T09:00:00',
                              'end_release_time': '2013-02-13T15:00:00',
                              'start_time_invalid': False,
                              'end_position': [144.664166, 13.441944, 0.0],
                              'start_position': [144.664166, 13.441944, 0.0],
                              },
                  'element_type': {'obj_type': ('gnome.spill.elements'
                                                '.ElementType'),
                                   'initializers': [{'obj_type': 'gnome.spill.elements.InitWindages',
                                                     'windage_range': [0.01,
                                                                       0.04],
                                                     'windage_persist': 900,
                                                     }
                                                    ]
                                   },
                  }

    wind_data = {'obj_type': 'gnome.environment.Wind',
                 'description': u'Wind Object',
                 'updated_at': '2014-03-26T14:52:45.385126',
                 'source_type': u'undefined',
                 'source_id': u'undefined',
                 'timeseries': [('2013-02-13T09:00:00', (1.0, 0.0)),
                                ('2013-02-13T10:00:00', (1.0, 45.0)),
                                ('2013-02-13T11:00:00', (1.0, 90.0)),
                                ('2013-02-13T12:00:00', (1.0, 120.0)),
                                ('2013-02-13T13:00:00', (1.0, 180.0)),
                                ('2013-02-13T14:00:00', (1.0, 270.0))],
                 'units': u'meter per second',
                 'latitude': 150,
                 'longitude': 15,
                 }

    water_data = {'obj_type': 'gnome.environment.Water',
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
                            'kinematic_viscosity': 'm^2/s'}
                  }

    evaporation_data = {'obj_type': u'gnome.weatherers.Evaporation',
                        'active_start': '-inf',
                        'active_stop': 'inf',
                        'on': True,
                        }

    dispersion_data = {'obj_type': u'gnome.weatherers.NaturalDispersion',
                       'active_start': '2013-02-13T15:00:00',
                       'active_stop': '2013-02-13T21:00:00',
                       'on': True,
                       }

    geojson_output_data = {'obj_type': ('gnome.outputters'
                                        '.TrajectoryGeoJsonOutput'),
                           'name': 'GeoJson',
                           'output_last_step': True,
                           'output_zero_step': True,
                           'output_dir': 'models/images'
                           }

    current_output_data = {'obj_type': ('gnome.outputters'
                                        '.CurrentGridGeoJsonOutput'),
                           'name': 'CurrentGrid',
                           'output_last_step': True,
                           'output_zero_step': True,
                           }

    weathering_output_data = {'obj_type': (u'gnome.outputters.weathering'
                                           '.WeatheringOutput'),
                              'name': u'WeatheringOutput',
                              'output_last_step': True,
                              'output_zero_step': True}

    def test_first_step(self):
        # We are testing our ability to generate the first step in a model run
        resp = self.testapp.get('/location/central-long-island-sound')

        assert 'name' in resp.json_body
        assert 'steps' in resp.json_body
        assert 'geometry' in resp.json_body
        assert 'coordinates' in resp.json_body['geometry']

        # OK, if we get this far, we should have an active model
        print 'test_first_step(): getting model...'
        resp = self.testapp.get('/model')
        model1 = resp.json_body

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # so what do we still need?
        # - maybe a wind and a windmover??? (optional)

        # - we need a spill
        print 'test_first_step(): creating spill...'
        resp = self.testapp.post_json('/spill', params=self.spill_data)
        spill = resp.json_body
        model1['spills'] = [spill]

        # - we need outputters
        print 'test_first_step(): creating outputters...'
        model1['outputters'] = [self.geojson_output_data,
                                self.weathering_output_data]

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert model1['spills'][0]['id'] == spill['id']

        # Alright, now we can try a first step.
        # This does not(should not?) require a step_id
        resp = self.testapp.get('/step')
        first_step = resp.json_body

        assert first_step['TrajectoryGeoJsonOutput']['step_num'] == 0

    def test_weathering_step(self):
        # We are testing our ability to generate the first step in a
        # weathering model run
        self.testapp.get('/location/central-long-island-sound')

        # OK, if we get this far, we should have an active model
        print 'test_weathering_step(): getting model...'
        resp = self.testapp.get('/model')
        model1 = resp.json_body

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # So what do we still need?
        # - we need a spill
        print 'test_weathering_step(): creating spill...'
        model1['spills'] = [self.spill_data]

        # - we need a weatherer
        print 'test_weathering_step(): creating weatherer...'
        model1['weatherers'] = [self.evaporation_data,
                                self.dispersion_data]

        # - we need outputters
        print 'test_weathering_step(): creating outputters...'
        model1['outputters'] = [self.geojson_output_data,
                                self.weathering_output_data]

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert 'id' in model1['spills'][0]
        assert 'id' in model1['weatherers'][0]
        assert 'id' in model1['outputters'][0]
        assert 'id' in model1['outputters'][1]

        resp = self.testapp.get('/step')
        first_step = resp.json_body

        assert first_step['TrajectoryGeoJsonOutput']['step_num'] == 0
        assert first_step['WeatheringOutput']['step_num'] == 0
        for v in first_step['WeatheringOutput'].values():
            if isinstance(v, dict):
                assert v['step_num'] == 0

    def test_weathering_step_with_rewind(self):
        # We are testing our ability to generate the first step in a
        # weathering model run
        self.testapp.get('/location/central-long-island-sound')

        # OK, if we get this far, we should have an active model
        print 'test_weathering_step(): getting model...'
        resp = self.testapp.get('/model')
        model1 = resp.json_body

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # So what do we still need?
        # - we need a spill
        print 'test_weathering_step(): creating spill...'
        model1['spills'] = [self.spill_data]
        model1['spills'][0]['amount_uncertainty_scale'] = 0.5

        model1['environment'].append(self.wind_data)
        model1['environment'].append(self.water_data)

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        # - we need weatherers
        wind_data = [e for e in model1['environment']
                     if e['obj_type'] == 'gnome.environment.wind.Wind'][0]
        water_data = [e for e in model1['environment']
                      if e['obj_type'] == 'gnome.environment.environment.Water'
                      ][0]

        print 'test_weathering_step(): creating weatherer...'
        self.evaporation_data['wind'] = wind_data
        self.evaporation_data['water'] = water_data
        model1['weatherers'] = [self.evaporation_data,
                                self.dispersion_data]

        # - we need outputters
        print 'test_weathering_step(): creating outputters...'
        model1['outputters'] = [self.geojson_output_data,
                                self.weathering_output_data]

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert 'id' in model1['spills'][0]
        assert 'id' in model1['weatherers'][0]
        assert 'id' in model1['outputters'][0]
        assert 'id' in model1['outputters'][1]

        resp = self.testapp.get('/step')
        first_step = resp.json_body

        assert first_step['TrajectoryGeoJsonOutput']['step_num'] == 0
        assert first_step['WeatheringOutput']['step_num'] == 0

        weathering_out = [v for v in first_step['WeatheringOutput'].values()
                          if isinstance(v, dict)]
        assert len(weathering_out) == 12
        for v in weathering_out:
            assert v['step_num'] == 0

        resp = self.testapp.get('/step')
        second_step = resp.json_body

        assert second_step['TrajectoryGeoJsonOutput']['step_num'] == 1
        assert second_step['WeatheringOutput']['step_num'] == 1

        weathering_out = [v for v in second_step['WeatheringOutput'].values()
                          if isinstance(v, dict)]
        assert len(weathering_out) == 12
        for v in weathering_out:
            assert v['step_num'] == 1

        resp = self.testapp.get('/rewind')
        rewind_response = resp.json_body
        assert rewind_response is None

        resp = self.testapp.get('/step')
        rewound_step = resp.json_body

        assert rewound_step['TrajectoryGeoJsonOutput']['step_num'] == 0
        assert rewound_step['WeatheringOutput']['step_num'] == 0

        weathering_out = [v for v in rewound_step['WeatheringOutput'].values()
                          if isinstance(v, dict)]
        assert len(weathering_out) == 12
        for v in weathering_out:
            assert v['step_num'] == 0

    def test_current_output_step(self):
        # We are testing our ability to generate the first step in a
        # weathering model run
        self.testapp.get('/location/central-long-island-sound')

        # OK, if we get this far, we should have an active model
        print 'test_weathering_step(): getting model...'
        resp = self.testapp.get('/model')
        model1 = resp.json_body

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # So what do we still need?
        # - we need a spill
        print 'test_weathering_step(): creating spill...'
        model1['spills'] = [self.spill_data]
        model1['spills'][0]['amount_uncertainty_scale'] = 0.5

        model1['environment'].append(self.wind_data)
        model1['environment'].append(self.water_data)

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        # - we need weatherers
        wind_data = [e for e in model1['environment']
                     if e['obj_type'] == 'gnome.environment.wind.Wind'][0]
        water_data = [e for e in model1['environment']
                      if e['obj_type'] == 'gnome.environment.environment.Water'
                      ][0]

        print 'test_weathering_step(): creating weatherer...'
        self.evaporation_data['wind'] = wind_data
        self.evaporation_data['water'] = water_data
        model1['weatherers'] = [self.evaporation_data,
                                self.dispersion_data]

        # - we need outputters
        print 'test_weathering_step(): creating outputters...'
        self.current_output_data['current_mover'] = model1['movers'][1]

        # print 'our current outputter data'
        # pp.pprint(self.current_output_data)

        model1['outputters'] = [self.geojson_output_data,
                                self.current_output_data,
                                self.weathering_output_data]

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert 'id' in model1['spills'][0]
        assert 'id' in model1['weatherers'][0]
        assert 'id' in model1['outputters'][0]
        assert 'id' in model1['outputters'][1]
        assert 'id' in model1['outputters'][2]

        resp = self.testapp.get('/step')
        first_step = resp.json_body

        assert first_step['TrajectoryGeoJsonOutput']['step_num'] == 0
        assert first_step['CurrentGridGeoJsonOutput']['step_num'] == 0
        assert first_step['WeatheringOutput']['step_num'] == 0

        current_grid_out = first_step['CurrentGridGeoJsonOutput']
        fc = current_grid_out['feature_collection']
        assert 'type' in fc
        assert fc['type'] == 'FeatureCollection'
        assert 'features' in fc
        assert len(fc['features']) > 0

        for feature in fc['features']:
            assert 'type' in feature
            assert feature['type'] == 'Feature'

            assert 'properties' in feature
            assert 'velocity' in feature['properties']

            assert 'geometry' in feature
            assert len(feature['geometry']) > 0

            geometry = feature['geometry']
            assert 'type' in geometry
            assert geometry['type'] == 'Point'

            assert 'coordinates' in geometry
            assert len(geometry['coordinates']) == 2

        resp = self.testapp.get('/step')
        second_step = resp.json_body

        assert second_step['TrajectoryGeoJsonOutput']['step_num'] == 1
        assert second_step['CurrentGridGeoJsonOutput']['step_num'] == 1
        assert second_step['WeatheringOutput']['step_num'] == 1

        current_grid_out = second_step['CurrentGridGeoJsonOutput']
        fc = current_grid_out['feature_collection']
        assert 'type' in fc
        assert fc['type'] == 'FeatureCollection'
        assert 'features' in fc
        assert len(fc['features']) > 0

        for feature in fc['features']:
            assert 'type' in feature
            assert feature['type'] == 'Feature'

            assert 'properties' in feature
            assert 'velocity' in feature['properties']

            assert 'geometry' in feature
            assert len(feature['geometry']) > 0

            geometry = feature['geometry']
            assert 'type' in geometry
            assert geometry['type'] == 'Point'

            assert 'coordinates' in geometry
            assert len(geometry['coordinates']) == 2


    @pytest.mark.slow
    def test_all_steps(self):
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

        model1['time_step'] = 900
        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        num_time_steps = model1['num_time_steps']

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # so what do we still need?
        # - maybe a wind and a windmover??? (optional)

        # - we need a spill
        print 'test_all_steps(): creating spill...'
        resp = self.testapp.post_json('/spill', params=self.spill_data)
        spill = resp.json_body
        model1['spills'] = [spill]

        # - we need an outputter
        print 'test_all_steps(): creating outputter...'
        # - we need outputters
        print 'test_weathering_step(): creating outputters...'
        model1['outputters'] = [self.geojson_output_data,
                                self.weathering_output_data]

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert model1['spills'][0]['id'] == spill['id']

        # Alright, now we can try to cycle through our steps.
        print 'num_steps = ', num_time_steps

        for s in range(num_time_steps):
            resp = self.testapp.get('/step')
            step = resp.json_body
            print '{0}, '.format(step['TrajectoryGeoJsonOutput']['step_num']),
            assert step['TrajectoryGeoJsonOutput']['step_num'] == s
            assert 'feature_collection' in step['TrajectoryGeoJsonOutput']

        # an additional call to /step should generate a 404
        resp = self.testapp.get('/step', status=404)

        print 'done!'
