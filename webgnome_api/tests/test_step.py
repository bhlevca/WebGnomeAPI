"""
Functional tests for the Gnome Location object Web API
"""
import datetime
import dateutil.parser

import pytest

from .base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)


class StepTest(FunctionalTestBase):
    '''
        Tests out the Gnome Location object API
    '''
    substance_data = {"adios_oil_id": "AD01759",
                      "name": "ALASKA NORTH SLOPE (MIDDLE PIPELINE)",
                      "bullwinkle_time": None,
                      "api": 29.9,
                      "molecular_weights": [{"sara_type": "Saturates",
                                             "g_mol": 73.68357055970264,
                                             "ref_temp_k": 313},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 63.07203818161141,
                                             "ref_temp_k": 313},
                                            {"sara_type": "Saturates",
                                             "g_mol": 91.28590469084087,
                                             "ref_temp_k": 353},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 79.28575654300448,
                                             "ref_temp_k": 353},
                                            {"sara_type": "Saturates",
                                             "g_mol": 111.21782045593451,
                                             "ref_temp_k": 393},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 97.81363430554806,
                                             "ref_temp_k": 393},
                                            {"sara_type": "Saturates",
                                             "g_mol": 133.75142397284813,
                                             "ref_temp_k": 433},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 118.95282475816097,
                                             "ref_temp_k": 433},
                                            {"sara_type": "Saturates",
                                             "g_mol": 159.22349825764528,
                                             "ref_temp_k": 473},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 143.07734277976434,
                                             "ref_temp_k": 473},
                                            {"sara_type": "Saturates",
                                             "g_mol": 238.776174385486,
                                             "ref_temp_k": 573},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 219.89701740947635,
                                             "ref_temp_k": 573},
                                            {"sara_type": "Saturates",
                                             "g_mol": 349.8842273437913,
                                             "ref_temp_k": 673},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 330.95381724488277,
                                             "ref_temp_k": 673},
                                            {"sara_type": "Saturates",
                                             "g_mol": 512.9196274962972,
                                             "ref_temp_k": 773},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 502.8745784181198,
                                             "ref_temp_k": 773},
                                            {"sara_type": "Saturates",
                                             "g_mol": 776.4793160510156,
                                             "ref_temp_k": 873},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 810.9321338867865,
                                             "ref_temp_k": 873},
                                            {"sara_type": "Saturates",
                                             "g_mol": 1309.47584568329,
                                             "ref_temp_k": 973},
                                            {"sara_type": "Aromatics",
                                             "g_mol": 1677.2879705369483,
                                             "ref_temp_k": 973}],
                      "cuts": [{"vapor_temp_k": 313,
                                "liquid_temp_k": None,
                                "fraction": 0.03},
                               {"vapor_temp_k": 353,
                                "liquid_temp_k": None,
                                "fraction": 0.07},
                               {"vapor_temp_k": 393,
                                "liquid_temp_k": None,
                                "fraction": 0.13},
                               {"vapor_temp_k": 433,
                                "liquid_temp_k": None,
                                "fraction": 0.19},
                               {"vapor_temp_k": 473,
                                "liquid_temp_k": None,
                                "fraction": 0.25},
                               {"vapor_temp_k": 573,
                                "liquid_temp_k": None,
                                "fraction": 0.42},
                               {"vapor_temp_k": 673,
                                "liquid_temp_k": None,
                                "fraction": 0.6},
                               {"vapor_temp_k": 773,
                                "liquid_temp_k": None,
                                "fraction": 0.76},
                               {"vapor_temp_k": 873,
                                "liquid_temp_k": None,
                                "fraction": 0.88},
                               {"vapor_temp_k": 973,
                                "liquid_temp_k": None,
                                "fraction": 0.95}],
                      "pour_point_min_k": 219,
                      "oil_seawater_interfacial_tension_ref_temp_k": 273,
                      "estimated": {"emulsion_water_fraction_max": True,
                                    "pour_point_max_k": False,
                                    "densities": False,
                                    "oil_water_interfacial_tension_n_m": False,
                                    "sara_fractions": True,
                                    "soluability": True,
                                    "flash_point_min_k": False,
                                    "sulphur_fraction": False,
                                    "flash_point_max_k": False,
                                    "api": False,
                                    "molecular_weights": True,
                                    "viscosities": True,
                                    "cuts": False,
                                    "oil_water_interfacial_tension_ref_temp_k": False,
                                    "adhesion_kg_m_2": False,
                                    "pour_point_min_k": False,
                                    "bullwinkle_fraction": True,
                                    "name": False},
                      "sulphur_fraction": 0.0116,
                      "oil_water_interfacial_tension_n_m": 0.0238,
                      "flash_point_max_k": 250,
                      "categories": [{"name": "Medium",
                                      "parent": {"name": "Crude"},
                                      "children": []}],
                      "adhesion_kg_m_2": 0.28,
                      "bullwinkle_fraction": 0.303,
                      "flash_point_min_k": 250,
                      "pour_point_max_k": 219,
                      "oil_seawater_interfacial_tension_n_m": 0,
                      "soluability": 0,
                      "emulsion_water_fraction_max": 0.9,
                      "sara_densities": [{"density": 1100,
                                          "sara_type": "Asphaltenes",
                                          "ref_temp_k": 1015},
                                         {"density": 1100,
                                          "sara_type": "Resins",
                                          "ref_temp_k": 1015},
                                         {"density": 586.832580809435,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 313},
                                         {"density": 610.8356003137033,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 353},
                                         {"density": 633.0873299844258,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 393},
                                         {"density": 653.8760102655268,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 433},
                                         {"density": 673.4207366641332,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 473},
                                         {"density": 717.8785538152601,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 573},
                                         {"density": 757.4217870352746,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 673},
                                         {"density": 793.218077458261,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 773},
                                         {"density": 826.0459124138969,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 873},
                                         {"density": 856.4533623013274,
                                          "sara_type": "Saturates",
                                          "ref_temp_k": 973},
                                         {"density": 704.1990969713219,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 313},
                                         {"density": 733.002720376444,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 353},
                                         {"density": 759.7047959813109,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 393},
                                         {"density": 784.6512123186321,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 433},
                                         {"density": 808.1048839969599,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 473},
                                         {"density": 861.4542645783122,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 573},
                                         {"density": 908.9061444423295,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 673},
                                         {"density": 951.8616929499133,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 773},
                                         {"density": 991.2550948966762,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 873},
                                         {"density": 1027.744034761593,
                                          "sara_type": "Aromatics",
                                          "ref_temp_k": 973}],
                      "densities": [{"ref_temp_k": 273,
                                     "kg_m_3": 887,
                                     "weathering": 0},
                                    {"ref_temp_k": 288,
                                     "kg_m_3": 876,
                                     "weathering": 0}],
                      "sara_fractions": [{"sara_type": "Resins",
                                          "ref_temp_k": 1015,
                                          "fraction": 0.07562177555384551},
                                         {"sara_type": "Asphaltenes",
                                          "ref_temp_k": 1015,
                                          "fraction": 0.016287321129049806},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 313,
                                          "fraction": 0.0147634532332906},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 313,
                                          "fraction": 0.0152365467667094},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 353,
                                          "fraction": 0.011437523613440248},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 353,
                                          "fraction": 0.02856247638655976},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 393,
                                          "fraction": 0.003713332652193215},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 393,
                                          "fraction": 0.05628666734780678},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 433,
                                          "fraction": 0},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 433,
                                          "fraction": 0.06},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 473,
                                          "fraction": 0},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 473,
                                          "fraction": 0.06},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 573,
                                          "fraction": 0.08499999999999999},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 573,
                                          "fraction": 0.08499999999999999},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 673,
                                          "fraction": 0.09},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 673,
                                          "fraction": 0.09},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 773,
                                          "fraction": 0.08000000000000002},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 773,
                                          "fraction": 0.08000000000000002},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 873,
                                          "fraction": 0.06},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 873,
                                          "fraction": 0.06},
                                         {"sara_type": "Saturates",
                                          "ref_temp_k": 973,
                                          "fraction": 0.014045451658552309},
                                         {"sara_type": "Aromatics",
                                          "ref_temp_k": 973,
                                          "fraction": 0.014045451658552309}],
                      "kvis": [{"m_2_s": 0.00003833145434047351,
                                "ref_temp_k": 273,
                                "weathering": 0},
                               {"m_2_s": 0.000018264840182648402,
                                "ref_temp_k": 288,
                                "weathering": 0}],
                      "k0y": 0.00000202,
                      "oil_water_interfacial_tension_ref_temp_k": 273,
                      }

    spill_data = {'obj_type': 'gnome.spill.spill.Spill',
                  'name': 'What a Name',
                  'on': True,
                  'amount': 1000,
                  'units': 'kg',
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
                  'substance': {'obj_type': 'gnome.spill.substance.NonWeatheringSubstance',
                                'initializers': [{'obj_type': 'gnome.spill.initializers.InitWindages',
                                                  'windage_range': [0.01,
                                                                    0.04],
                                                  'windage_persist': 900,
                                                  }]
                               },
                  }

    wind_data = {'obj_type': 'gnome.environment.Wind',
                 'description': 'Wind Object',
                 'updated_at': '2014-03-26T14:52:45.385126',
                 'source_type': 'undefined',
                 'source_id': 'undefined',
                 'timeseries': [('2013-02-13T09:00:00', (1.0, 0.0)),
                                ('2013-02-13T10:00:00', (1.0, 45.0)),
                                ('2013-02-13T11:00:00', (1.0, 90.0)),
                                ('2013-02-13T12:00:00', (1.0, 120.0)),
                                ('2013-02-13T13:00:00', (1.0, 180.0)),
                                ('2013-02-13T14:00:00', (1.0, 270.0))],
                 'units': 'meter per second',
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

    waves_data = {'name': 'Waves',
                  'obj_type': 'gnome.environment.waves.Waves',
                  'water': None,
                  'wind': None}

    evaporation_data = {'obj_type': 'gnome.weatherers.Evaporation',
                        'active_range': ('-inf', 'inf'),
                        'on': True,
                        }

    dispersion_data = {'obj_type': 'gnome.weatherers.NaturalDispersion',
                       'active_range': ('2013-02-13T15:00:00',
                                        '2013-02-13T21:00:00'),
                       'on': True,
                       }

    skimmer_data = {"obj_type": "gnome.weatherers.cleanup.Skimmer",
                    "name": "Skimmer #1",
                    "active_range": ("2013-02-13T15:00:00",
                                     "2013-02-15T15:00:00"),
                    "efficiency": 0.2,
                    "amount": "200",
                    "units": "bbl",
                    }

    geojson_output_data = {'obj_type': ('gnome.outputters'
                                        '.TrajectoryGeoJsonOutput'),
                           'name': 'GeoJson',
                           'output_last_step': True,
                           'output_zero_step': True,
                           'output_dir': None
                           }

    current_output_data = {'obj_type': ('gnome.outputters'
                                        '.CurrentJsonOutput'),
                           'name': 'CurrentGrid',
                           'output_last_step': True,
                           'output_zero_step': True,
                           }

    weathering_output_data = {'obj_type': ('gnome.outputters.weathering'
                                           '.WeatheringOutput'),
                              'name': 'WeatheringOutput',
                              'output_last_step': True,
                              'output_zero_step': True}

    def test_first_step(self):
        # We are testing our ability to generate the first step in a model run
        resp = self.testapp.get('/location/central-long-island-sound-ny')

        assert 'name' in resp.json_body
        assert 'steps' in resp.json_body
        assert 'geometry' in resp.json_body
        assert 'coordinates' in resp.json_body['geometry']

        # OK, if we get this far, we should have an active model
        print('test_first_step(): getting model...')
        resp = self.testapp.get('/model')
        model1 = resp.json_body
        model_start_time = model1['start_time']

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # so what do we still need?
        # - maybe a wind and a windmover??? (optional)

        # - we need a spill
        print('test_first_step(): creating spill...')
        resp = self.testapp.post_json('/spill', params=self.spill_data)
        spill = resp.json_body
        spill['release']['release_time'] = model_start_time
        spill['release']['end_release_time'] = model_start_time
        spill['water'] = self.water_data
        model1['spills'] = [spill]

        # - we need outputters
        print('test_first_step(): creating outputters...')
        model1['outputters'] = [self.geojson_output_data,
                                self.weathering_output_data]

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert model1['spills'][0]['id'] == spill['id']

        # Alright, now we can try a first step.
        # This does not(should not?) require a step_id
        resp = self.testapp.get('/step')
        first_step = resp.json_body

        assert first_step['step_num'] == 0

    def test_weathering_step(self):
        # We are testing our ability to generate the first step in a
        # weathering model run
        self.testapp.get('/location/central-long-island-sound-ny')

        # OK, if we get this far, we should have an active model
        print('test_weathering_step(): getting model...')
        resp = self.testapp.get('/model')
        model1 = resp.json_body
        model_start_time = model1['start_time']

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # So what do we still need?
        # - we need a spill
        print('test_weathering_step(): creating spill...')
        model1['spills'] = [self.spill_data]
        model1['spills'][0]['release']['release_time'] = model_start_time
        model1['spills'][0]['release']['end_release_time'] = model_start_time

        model1['environment'].append(self.wind_data)
        model1['environment'].append(self.water_data)

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        # - we need weatherers
        wind_data = [e for e in model1['environment']
                     if e['obj_type'] == 'gnome.environment.wind.Wind'][0]
        water_data = [e for e in model1['environment']
                      if e['obj_type'] == 'gnome.environment.water.Water'
                      ][0]

        print('test_weathering_step(): creating weatherer...')
        self.waves_data['wind'] = wind_data
        self.waves_data['water'] = water_data
        model1['environment'].append(self.waves_data)

        self.evaporation_data['wind'] = wind_data
        self.evaporation_data['water'] = water_data
        self.dispersion_data['water'] = water_data
        self.dispersion_data['waves'] = self.waves_data

        model1['weatherers'] = [self.evaporation_data,
                                self.dispersion_data]

        # - we need outputters
        print('test_weathering_step(): creating outputters...')
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

        assert first_step['step_num'] == 0

    def test_weathering_step_with_rewind(self):
        # We are testing our ability to generate the first step in a
        # weathering model run
        self.testapp.get('/location/central-long-island-sound-ny')

        # OK, if we get this far, we should have an active model
        print('test_weathering_step(): getting model...')
        resp = self.testapp.get('/model')
        model1 = resp.json_body
        model_start_time = model1['start_time']

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # So what do we still need?
        # - we need a spill
        print('test_weathering_step(): creating spill...')
        model1['spills'] = [self.spill_data]
        # amount uncertainty no longer functional on Windows
        #model1['spills'][0]['amount_uncertainty_scale'] = 0.5
        model1['spills'][0]['release']['release_time'] = model_start_time
        model1['spills'][0]['release']['end_release_time'] = model_start_time

        model1['environment'].append(self.wind_data)
        model1['environment'].append(self.water_data)

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        # - we need weatherers
        wind_data = [e for e in model1['environment']
                     if e['obj_type'] == 'gnome.environment.wind.Wind'][0]
        water_data = [e for e in model1['environment']
                      if e['obj_type'] == 'gnome.environment.water.Water'
                      ][0]

        print('test_weathering_step(): creating weatherer...')
        self.waves_data['wind'] = wind_data
        self.waves_data['water'] = water_data
        model1['environment'].append(self.waves_data)

        self.evaporation_data['wind'] = wind_data
        self.evaporation_data['water'] = water_data
        self.dispersion_data['water'] = water_data
        self.dispersion_data['waves'] = self.waves_data

        model1['weatherers'] = [self.evaporation_data,
                                self.dispersion_data]

        # - we need outputters
        print('test_weathering_step(): creating outputters...')
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

        assert first_step['step_num'] == 0

        weathering_out = [v for v in list(first_step['WeatheringOutput'].values())
                          if isinstance(v, dict)]
        assert len(weathering_out) == 12

        resp = self.testapp.get('/step')
        second_step = resp.json_body

        assert second_step['step_num'] == 1

        weathering_out = [v for v in list(second_step['WeatheringOutput'].values())
                          if isinstance(v, dict)]
        assert len(weathering_out) == 12

        resp = self.testapp.get('/rewind')
        rewind_response = resp.json_body
        assert rewind_response is None

        resp = self.testapp.get('/step')
        rewound_step = resp.json_body

        assert rewound_step['step_num'] == 0

        weathering_out = [v for v in list(rewound_step['WeatheringOutput'].values())
                          if isinstance(v, dict)]
        assert len(weathering_out) == 12

    def test_current_output_step(self):
        # We are testing our ability to generate the first step in a
        # weathering model run
        self.testapp.get('/location/central-long-island-sound-ny')

        # OK, if we get this far, we should have an active model
        print('test_weathering_step(): getting model...')
        resp = self.testapp.get('/model')
        model1 = resp.json_body
        model_start_time = model1['start_time']

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # So what do we still need?
        # - we need a spill
        print('test_weathering_step(): creating spill...')
        model1['spills'] = [self.spill_data]
        # amount uncertainty no longer functional on Windows
        #model1['spills'][0]['amount_uncertainty_scale'] = 0.5 
        model1['spills'][0]['release']['release_time'] = model_start_time
        model1['spills'][0]['release']['end_release_time'] = model_start_time

        model1['environment'].append(self.wind_data)
        model1['environment'].append(self.water_data)

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        # - we need weatherers
        wind_data = [e for e in model1['environment']
                     if e['obj_type'] == 'gnome.environment.wind.Wind'][0]
        water_data = [e for e in model1['environment']
                      if e['obj_type'] == 'gnome.environment.water.Water'
                      ][0]

        print('test_weathering_step(): creating weatherer...')
        self.waves_data['wind'] = wind_data
        self.waves_data['water'] = water_data
        model1['environment'].append(self.waves_data)

        self.evaporation_data['wind'] = wind_data
        self.evaporation_data['water'] = water_data
        self.dispersion_data['water'] = water_data
        self.dispersion_data['waves'] = self.waves_data

        model1['weatherers'] = [self.evaporation_data,
                                self.dispersion_data]

        # - we need outputters
        print('test_weathering_step(): creating outputters...')
        self.current_output_data['current_movers'] = [model1['movers'][1]]

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

        assert first_step['step_num'] == 0

        current_grid_out = first_step['CurrentJsonOutput']

        for _k, v in current_grid_out.items():

            assert set(v.keys()).issuperset(('direction', 'magnitude'))
            direction, magnitude = [v[sub_key]
                                    for sub_key in ('direction', 'magnitude')]

            assert all([isinstance(d, float) for d in direction])
            assert all([isinstance(m, float) for m in magnitude])
            assert len(direction) == len(magnitude)

        resp = self.testapp.get('/step')
        second_step = resp.json_body

        print(('total_response_time: ',
               second_step['total_response_time']))
        print(('uncertain_response_time: ',
               second_step['uncertain_response_time']))

        assert second_step['step_num'] == 1

        current_grid_out = second_step['CurrentJsonOutput']

        for _k, v in current_grid_out.items():

            assert set(v.keys()).issuperset(('direction', 'magnitude'))
            direction, magnitude = [v[sub_key]
                                    for sub_key in ('direction', 'magnitude')]

            assert all([isinstance(d, float) for d in direction])
            assert all([isinstance(m, float) for m in magnitude])
            assert len(direction) == len(magnitude)

    def test_current_output_performance(self):
        # We are testing our ability to generate the first step in a
        # weathering model run
        self.testapp.get('/location/new-york-harbor-ny')

        # OK, if we get this far, we should have an active model
        print('test_weathering_step(): getting model...')
        resp = self.testapp.get('/model')
        model1 = resp.json_body
        model_start_time = model1['start_time']

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # So what do we still need?
        # - we need a spill
        print('\n\ndefining our spill data')
        substance = {"obj_type": 'gnome.spill.substance.GnomeOil',
                     "initializers": [{"windage_range": [0.01, 0.04],
                                       "obj_type": 'gnome.spill.initializers.InitWindages',
                                       "windage_persist": 900}]
                        }
        substance.update(self.substance_data)

        spill_data = {"release": {"json_": "webapi",
                                  "obj_type": ("gnome.spill.release"
                                               ".PointLineRelease"),
                                  "end_position": [-73.83952178907545,
                                                   40.4626050585251, 0],
                                  "start_position": [-73.83952178907545,
                                                     40.4626050585251, 0],
                                  "num_elements": 1000,
                                  "num_released": 0,
                                  "start_time_invalid": True,
                                  "release_time": "2015-05-15T16:00:00",
                                  "num_per_timestep": None,
                                  "end_release_time": "2015-05-15T16:00:00"},
                      "on": True,
                      "obj_type": "gnome.spill.spill.Spill",
                      "substance": substance,
                      "name": "Spill #1",
                      "amount": 2000,
                      "units": "bbl",
                      "amount_uncertainty_scale": 0
                      }

        print('test_weathering_step(): creating spill...')
        model1['spills'] = [spill_data]
        model1['spills'][0]['release']['release_time'] = model_start_time
        model1['spills'][0]['release']['end_release_time'] = model_start_time

        model1['environment'].append(self.wind_data)
        model1['environment'].append(self.water_data)

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        # - we need weatherers
        wind_data = [e for e in model1['environment']
                     if e['obj_type'] == 'gnome.environment.wind.Wind'][0]
        water_data = [e for e in model1['environment']
                      if e['obj_type'] == 'gnome.environment.water.Water'
                      ][0]

        print('test_weathering_step(): creating weatherer...')
        self.waves_data['wind'] = wind_data
        self.waves_data['water'] = water_data
        model1['environment'].append(self.waves_data)
        model1['spills'][0]['water'] = water_data

        self.evaporation_data['wind'] = wind_data
        self.evaporation_data['water'] = water_data

        self.dispersion_data['water'] = water_data
        self.dispersion_data['waves'] = self.waves_data

        model1['weatherers'] = [self.evaporation_data,
                                self.dispersion_data]

        # - we need outputters
        print('test_weathering_step(): creating outputters...')
        model1['outputters'] = [self.geojson_output_data,
                                self.weathering_output_data]

        print('\n\nUpdating our model...')
        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        print('\n\nOur substance returned data...')
        pp.pprint(model1['spills'][0]['substance'])

        assert 'id' in model1['spills'][0]
        assert 'id' in model1['weatherers'][0]
        assert 'id' in model1['outputters'][0]
        assert 'id' in model1['outputters'][1]

        resp = self.testapp.get('/step')
        first_step = resp.json_body

        assert first_step['step_num'] == 0

    @pytest.mark.slow
    def test_all_steps(self):
        # We are testing our ability to generate the first step in a model run
        resp = self.testapp.get('/location/central-long-island-sound-ny')

        assert 'name' in resp.json_body
        assert 'steps' in resp.json_body
        assert 'geometry' in resp.json_body
        assert 'coordinates' in resp.json_body['geometry']

        # OK, if we get this far, we should have an active model
        print('test_all_steps(): getting model...')
        resp = self.testapp.get('/model')
        model1 = resp.json_body
        model_start_time = model1['start_time']

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
        print('test_all_steps(): creating spill...')
        resp = self.testapp.post_json('/spill', params=self.spill_data)
        spill = resp.json_body
        model1['spills'] = [spill]
        model1['spills'][0]['release']['release_time'] = model_start_time
        model1['spills'][0]['release']['end_release_time'] = model_start_time

        # - we need an outputter
        print('test_all_steps(): creating outputter...')
        # - we need outputters
        print('test_weathering_step(): creating outputters...')
        model1['outputters'] = [self.geojson_output_data,
                                self.weathering_output_data]

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert model1['spills'][0]['id'] == spill['id']

        # Alright, now we can try to cycle through our steps.
        print('num_steps = ', num_time_steps)

        for s in range(num_time_steps):
            resp = self.testapp.get('/step')
            step = resp.json_body
            print('{0}, '.format(step['step_num']), end=' ')
            assert step['step_num'] == s

            assert 'TrajectoryGeoJsonOutput' in step
            traj_out = step['TrajectoryGeoJsonOutput']
            for output_key in ('certain', 'uncertain'):
                print(list(traj_out[output_key].keys()))

                assert 'features' in traj_out[output_key]
                for f in traj_out[output_key]['features']:
                    print(list(f.keys()))

                    assert 'geometry' in f
                    print(list(f['geometry'].keys()))

                    assert 'coordinates' in f['geometry']
                    print(f['geometry']['coordinates'])

                    assert 'properties' in f
                    print(f['properties'])
                    assert f['properties']['status_code'] == 2
                    assert f['properties']['spill_num'] == 0
                    assert f['properties']['sc_type'] == 'forecast'

        # an additional call to /step should generate a 404
        resp = self.testapp.get('/step', status=404)

        print('done!')

    @pytest.mark.slow
    def test_full_run(self):
        '''
            Testing the full_run api
        '''
        # We are testing our ability to generate the first step in a
        # weathering model run
        self.testapp.get('/location/new-york-harbor-ny')

        # OK, if we get this far, we should have an active model
        print('test_weathering_step(): getting model...')
        resp = self.testapp.get('/model')
        model1 = resp.json_body
        print('model start time:', model1['start_time'])
        start_time = dateutil.parser.parse(model1['start_time'])

        duration = 5 * 24 * 60 * 60
        model1['duration'] = '{}'.format(float(duration))
        print(('model duration: {} hours'
               .format(float(model1['duration']) / 60 / 60)))

        model1['time_step'] = 900.0
        print(('model timestep: {} seconds'.format(model1['time_step'])))

        # The location file we selected should have:
        # - a registered map
        # - a registered Tide
        # - a registered RandomMover
        # - a registered CatsMover

        # So what do we still need?
        # - we need a spill
        print('\n\ndefining our spill data')
        substance = {"obj_type": "gnome.spill.substance.GnomeOil",
                     "initializers": [{"windage_range": [0.01, 0.04],
                                       "obj_type": "gnome.spill.initializers.InitWindages",
                                       "windage_persist": 900}]
                     }
        substance.update(self.substance_data)

        spill_data = {"release": {"json_": "webapi",
                                  "obj_type": ("gnome.spill.release"
                                               ".PointLineRelease"),
                                  "end_position": [-74.0280406367412,
                                                   40.5376381774569, 0],
                                  "start_position": [-74.0280406367412,
                                                     40.5376381774569, 0],
                                  "num_elements": 1000,
                                  "num_released": 0,
                                  "start_time_invalid": True,
                                  "release_time": start_time.isoformat(),
                                  "num_per_timestep": None,
                                  "end_release_time": start_time.isoformat()},
                      "on": True,
                      "obj_type": "gnome.spill.spill.Spill",
                      "substance": substance,
                      "name": "Spill #1",
                      "amount": 2000,
                      "units": "bbl",
                      "amount_uncertainty_scale": 0
                      }

        print('test_weathering_step(): creating spill...')
        model1['spills'] = [spill_data]

        model1['environment'].append(self.wind_data)

        # so the timeseries for our wind needs to encompass
        # the entire model duration now.
        corrected_ts = []
        for h in range(int((duration / 60 / 60) + 1)):
            ts_len = len(self.wind_data['timeseries'])

            corrected_time = (start_time +
                              datetime.timedelta(hours=h)
                              ).isoformat()
            corrected_ts.append((corrected_time,
                                 self.wind_data['timeseries'][h % ts_len][1]))

        self.wind_data['timeseries'] = corrected_ts

        model1['environment'].append(self.water_data)

        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        # - we need weatherers
        wind_data = [e for e in model1['environment']
                     if e['obj_type'] == 'gnome.environment.wind.Wind'][0]
        water_data = [e for e in model1['environment']
                      if e['obj_type'] == 'gnome.environment.water.Water'
                      ][0]

        print('test_weathering_step(): creating weatherer...')
        self.waves_data['wind'] = wind_data
        self.waves_data['water'] = water_data
        model1['environment'].append(self.waves_data)
        model1['spills'][0]['water'] = water_data

        self.evaporation_data['wind'] = wind_data
        self.evaporation_data['water'] = water_data

        self.dispersion_data['water'] = water_data
        self.dispersion_data['waves'] = self.waves_data

        self.skimmer_data['water'] = water_data
        self.skimmer_data['active_range'] = (start_time.isoformat(),
                                             (start_time +
                                              datetime.timedelta(days=1))
                                             .isoformat())

        model1['weatherers'] = [self.evaporation_data,
                                self.dispersion_data,
                                self.skimmer_data]

        # - we need outputters
        print('test_weathering_step(): creating outputters...')
        model1['outputters'] = [self.geojson_output_data,
                                self.weathering_output_data]

        print('\n\nUpdating our model...')
        resp = self.testapp.put_json('/model', params=model1)
        model1 = resp.json_body

        assert 'id' in model1['spills'][0]
        assert 'id' in model1['weatherers'][0]
        assert 'id' in model1['outputters'][0]
        assert 'id' in model1['outputters'][1]

        num_time_steps = model1['num_time_steps']
        expected_final_step = num_time_steps - 1

        # First we check the normal skimmed amount when we run the model
        # as normal
        for s in range(num_time_steps):
            resp = self.testapp.get('/step')
            step = resp.json_body
            assert step['step_num'] == s

        print('final step with response options active:')
        print('{0}, '.format(step['step_num']), end=' ')
        pp.pprint(step['WeatheringOutput'])

        assert 'nominal' in step['WeatheringOutput']
        assert 'skimmed' in step['WeatheringOutput']['nominal']
        assert step['WeatheringOutput']['nominal']['skimmed'] > 0.0
        skimmed_amt = step['WeatheringOutput']['nominal']['skimmed']

        # next we perform the full run without response options and then
        # check that nothing was skimmed.
        resp = self.testapp.post_json('/full_run',
                                      params={'response_on': False})
        final_step = resp.json_body

        print('\n\nour final step with response options inactive:')
        pp.pprint(final_step['WeatheringOutput'])

        assert final_step['step_num'] == expected_final_step
        assert 'nominal' in final_step['WeatheringOutput']
        assert 'skimmed' not in final_step['WeatheringOutput']['nominal']

        # Next we rewind the model and then re-run it as normal to
        # make sure that the skimmer was re-enabled after the full run.
        resp = self.testapp.get('/rewind')
        rewind_response = resp.json_body
        assert rewind_response is None

        for s in range(num_time_steps):
            resp = self.testapp.get('/step')
            step = resp.json_body
            assert step['step_num'] == s

        print('\n\nfinal step with response options active:')
        print('{0}, '.format(step['step_num']), end=' ')
        pp.pprint(step['WeatheringOutput'])

        assert 'nominal' in step['WeatheringOutput']
        assert 'skimmed' in step['WeatheringOutput']['nominal']
        assert step['WeatheringOutput']['nominal']['skimmed'] == skimmed_amt
