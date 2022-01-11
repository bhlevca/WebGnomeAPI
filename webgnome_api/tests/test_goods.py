"""
tests of the "GOODS" functionality

that is, getting maps, currents, etc for the model runs
"""

import os
import zipfile
from pathlib import Path

from gnome.model import Model

from .base import FunctionalTestBase, MODELS_DIR

import pytest


@pytest.mark.skip
class GetMapTest(FunctionalTestBase):
    '''
    Tests out getting a map from the GOODS API
    '''

    def test_get_map(self):
        resp = self.testapp.post_json('/session')
        req_session = resp.json_body['id']

        # what should this request look like ???

        self.testapp.post('/goods', {'session': req_session},
                          )
        assert False


