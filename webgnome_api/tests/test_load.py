"""
Functional tests for the Gnome Location object Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from base import FunctionalTestBase


class LoadModelTest(FunctionalTestBase):
    '''
        Tests out the Gnome Location object API
    '''
    def test_file_upload(self):
        # OK, if we get this far, we should have an active model
        resp = self.testapp.get('/model')
        model = resp.json_body
        print 'initial model:'
        pp.pprint(model)

        for c in ('environment', 'map', 'water',
                  'movers', 'outputters', 'spills', 'weatherers'):
            assert model['Model'][c] is None

        field_name = 'new_model'
        file_name = 'models/Model.zip'

        self.testapp.post('/load',
                          upload_files=[(field_name, file_name,)]
                          )

        resp = self.testapp.get('/model')
        model = resp.json_body
        print 'new model:'
        pp.pprint(model)

        for c in ('environment', 'map', 'water',
                  'movers', 'outputters', 'spills', 'weatherers'):
            assert model[c] is not None
