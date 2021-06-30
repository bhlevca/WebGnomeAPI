"""
Security tests for the Gnome Location object Web API

These are not exhaustive.
"""
import pytest

from .base import FunctionalTestBase

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)


class HTMLSecurityTest(FunctionalTestBase):
    def test_incoming_HTML(self):
        req_data = {'obj_type': 'gnome.model.Model',
                    'cache_enabled': False,
                    'duration': 86400.0,
                    'start_time': '2014-04-09T15:00:00',
                    'time_step': 900.0,
                    'uncertain': False,
                    'weathering_substeps': 1,
                    'environment': [],
                    'movers': [],
                    'outputters': [],
                    'spills': [],
                    'weatherers': [],
                    'name': '<script>alert(0)<script>',
                    'id': '"<script><script>"'
                    }
        resp = self.testapp.post_json('/<script>model', req_data)
        assert '<' not in resp.json_body['name'] 