"""
Functional tests for the Gnome Location object Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

import os
from base import FunctionalTestBase


class LoadModelTest(FunctionalTestBase):
    '''
        Tests out the Gnome Location object API
    '''
    def test_file_upload(self):
        # OK, if we get this far, we should have an active model
        print 'current directory:', os.getcwd()

        field_name = 'new_model'
        file_name = 'models/Model.zip'

        resp = self.testapp.post('/load',
                                 upload_files=[(field_name, file_name,)]
                                 )

        print resp
        raise
