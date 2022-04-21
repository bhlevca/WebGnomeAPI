"""
tests of the "GOODS" functionality

that is, getting maps, currents, etc for the model runs

We really need more tests!

"""

import os
import zipfile
from pathlib import Path
import json

from gnome.model import Model

from .base import FunctionalTestBase, MODELS_DIR

import pytest


# @pytest.mark.skip
class GetMapTest(FunctionalTestBase):
    '''
    Tests of getting a map from the GOODS API

    There should probably be tests of various failing conditions.
    '''

    def test_get_map(self):
        """
        a test of getting a single map

        Note that this does not test if the created file is valid

        That should be tested in the goods / libgoods code.
        """
        # This is what the current request looks like
        # it's passing it on through to GOODS
        # the request should be updated with our "new" API

        req_params = {'err_placeholder':'',
                      'NorthLat': 47.06693175688763,
                      'WestLon': -124.26942110656861,
                      'EastLon': -123.6972360021842,
                      'SouthLat': 46.78488364986247,
                      'xDateline': 0,
                      'resolution': 'i',
                      'shoreline': 'GSHHS',
                      'submit': 'Get Map',
                      }

        resp = self.testapp.post('/goods/maps', req_params)

        resp = resp.json_body

        filename = resp[1]
        local_path = Path(resp[0])

        # This might be a bit fragile, but...
        session_id = self.testapp.post('/session').json_body['id']
        expected_path = MODELS_DIR / "session" / session_id / filename
        print(local_path.resolve())
        print(expected_path.resolve())

        # did it put it in the right place?
        assert local_path.resolve() == expected_path.resolve()
        # is there an actual file there?
        assert expected_path.is_file()
        # is it non-empty?
        assert expected_path.stat().st_size > 0

        # maybe check creation time, or ???

@pytest.mark.skip("not functional right now")
class GetCurrentsTest(FunctionalTestBase):
    '''
    Tests of getting a netcdf file of currents from the webgnomeAPI

    via the libgoods system

    There should probably be tests of various failing conditions.
    '''

    def test_get_current_netcdf(self):
        """
        a test of getting a netcdf file of currents

        """
        # This is what the current request looks like
        # it's passing it on through to GOODS
        # the request should be updated with our "new" API

        req_params = {'err_placeholder':'',
                      'model_name': 'dummy_cur',
                      'NorthLat': 34.0,
                      'WestLon': -119.0,
                      'EastLon': -117.5,
                      'SouthLat': 33.0,
                      'xDateline': 0,
                      'resolution': 'i',
                      'submit': 'Get Map',
                      }

        resp = self.testapp.post('/goods/currents', req_params)

        resp = resp.json_body

        local_path = Path(resp)
        filename = local_path.name

        # This might be a bit fragile, but...
        session_id = self.testapp.post('/session').json_body['id']
        expected_path = MODELS_DIR / "session" / session_id / filename

        # did it put it in the right place?
        local_path = local_path.resolve()
        expected_path = expected_path.resolve()
        assert local_path == expected_path
        # is there an actual file there?
        assert expected_path.is_file()
        # is it non-empty?
        assert expected_path.stat().st_size > 0

@pytest.mark.skip("not functional right now")
class ListModels(FunctionalTestBase):
    '''
    Tests of getting a netcdf file of currents from the webgnomeAPI

    via the libgoods system

    There should probably be tests of various failing conditions.
    '''

    def test_list_models(self):
        """
        tests getting the metadata of the models
        """
        # This is what the current request looks like
        # it's passing it on through to GOODS
        # the request should be updated with our "new" API


        # should there be some parameters to the request?
        resp = self.testapp.get('/goods/list_models')

        resp = resp.json_body

        print(resp)
        # should we hard-code what's expected
        assert len(resp) > 0

        # just checking that we got what looks like the right dicts.
        for model in resp:
            assert 'identifier' in model
            assert 'name' in model
            assert 'bounding_box' in model
            assert 'bounding_poly' in model

