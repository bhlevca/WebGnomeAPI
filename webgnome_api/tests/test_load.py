"""
Functional tests for the Gnome Location object Web API
"""
import os
import zipfile
from pathlib import Path

from .base import FunctionalTestBase, MODELS_DIR

import pytest


TEST_SAVEFILE = str(MODELS_DIR / "long_island_sound.gnome")
TEST_UPLOAD_SAVEFILE = str(MODELS_DIR / "SaveModel.gnome")


class LoadModelTest(FunctionalTestBase):
    '''
    Tests out the Gnome Location object API
    '''
    def test_file_upload(self):
        resp = self.testapp.get('/model')
        model = resp.json_body

        for c in ('environment', 'map',
                  'movers', 'outputters', 'spills', 'weatherers'):
            assert model['Model'][c] is None

        field_name = 'new_model'
        file_name = TEST_SAVEFILE

        self.testapp.post('/upload', {'session': '1234'},
                          upload_files=[(field_name, file_name,)]
                          )

        resp = self.testapp.get('/model')
        model = resp.json_body

        for c in ('environment', 'map',
                  'movers', 'outputters', 'spills', 'weatherers'):
            assert model[c] is not None
            
    @pytest.mark.xfail
    def test_file_download(self):
        # first we load the model from our zipfile.
        field_name = 'new_model'
        test_file = TEST_SAVEFILE
        save_file = TEST_UPLOAD_SAVEFILE

        resp = self.testapp.post_json('/session')
        req_session = resp.json_body['id']

        self.testapp.post('/upload', {'session': req_session},
                          upload_files=[(field_name, test_file,)]
                          )

        resp = self.testapp.get('/model')
        model = resp.json_body

        for c in ('environment', 'map',
                  'movers', 'outputters', 'spills', 'weatherers'):
            assert model[c] is not None

        # next, we download the model as a zipfile.
        resp = self.testapp.get('/download')

        with open(save_file, 'wb') as file_:
            file_.write(resp.body)

        assert zipfile.is_zipfile(save_file)

        z_in = zipfile.ZipFile(test_file)
        z_out = zipfile.ZipFile(save_file)

        for info_in, info_out in zip(sorted(z_in.infolist(),
                                            key=lambda x: x.filename),
                                     sorted(z_out.infolist(),
                                            key=lambda x: x.filename)):
            print(((info_in.filename, info_out.filename),
                   (info_in.file_size, info_out.file_size)
                   ))

            assert info_in.filename == info_out.filename
            #assert info_in.file_size == info_out.file_size

            # unique IDs inside our files prevent us from verifying the
            # contents of our .json files
            # assert info_in.CRC == info_out.CRC

        z_in.close()
        z_out.close()

        os.remove(save_file)
