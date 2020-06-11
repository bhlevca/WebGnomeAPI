"""
Functional tests for the Gnome Map object Web API
"""
from os.path import basename
import webtest
import ujson

from base import FunctionalTestBase


class MapTestBase(FunctionalTestBase):
    '''
        Tests out the Gnome Map object API
    '''
    req_data = {'obj_type': 'gnome.maps.map.MapFromBNA',
                'filename': 'models/Test.bna',
                'refloat_halflife': 1.0
                }
    fields_to_check = ('id', 'obj_type', 'filename', 'refloat_halflife')
    """
    def test_goods_map(self):
        req = self.req_data.copy()
        req['filename'] = 'goods:Test.bna'
        resp = self.testapp.post_json('/map', params=req)
        map1 = resp.json_body

        # just some checks to see that we got our map
        assert len(map1['map_bounds']) == 4
        assert basename(map1['filename']) == 'Test.bna'

    def test_remote_map(self):
        req = self.req_data.copy()
        req['filename'] = 'https://gnome.orr.noaa.gov/goods/bnas/newyork.bna'
        resp = self.testapp.post_json('/map', params=req)
        map1 = resp.json_body

        # just some checks to see that we got our map
        assert len(map1['map_bounds']) == 4
        assert basename(map1['filename']) == 'newyork.bna'
    """
    def test_get_no_id(self):
        resp = self.testapp.get('/map')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/map/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create the object by performing a post
        # 2. get the valid id from the response
        # 3. perform an additional get of the object with a valid id
        # 4. check that our new JSON response matches the one from the create
        self.setup_map_file()
        resp1 = self.testapp.post_json('/map', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/map/{0}'.format(obj_id))

        for k in self.fields_to_check:
            assert resp2.json_body[k] == resp1.json_body[k]

    def test_post_no_payload(self):
        self.testapp.post_json('/map', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/map', status=400)

    def test_put_no_id(self):
        self.testapp.put_json('/map', params=self.req_data,
                              status=404)

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/map', params=params,
                              status=404)

    def test_put_valid_id(self):
        # 1. create the object by performing a post
        # 2. get the valid id from the response
        # 3. update the properties in the JSON response
        # 4. update the object by performing a put with a valid id
        # 5. check that our new properties are in the new JSON response
        self.setup_map_file()
        resp = self.testapp.post_json('/map', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/map', params=req_data)
        self.check_updates(resp.json_body)

    def test_file_upload(self):
        file_names = ['models/Test.bna',]
        self.setup_map_file()
        resp = self.testapp.post('/map/upload',
                                 {'session': '1234',
                                  'file_list': ujson.dumps(file_names),
                                  'name':'Test',
                                  'obj_type':'gnome.maps.map.MapFromBNA'}
                                 )
        map_obj = resp.json_body

        assert len(map_obj['map_bounds']) == 4
        assert basename(map_obj['filename'])[:4] == 'Test'
        assert basename(map_obj['filename'])[-4:] == '.bna'

    def test_get_raster(self):
        self.setup_map_file()
        resp1 = self.testapp.post_json('/map', params=self.req_data)

        obj_id = resp1.json_body['id']
        #resp2 = self.testapp.get('/map/{0}/raster'.format(obj_id))
        #JAH: Can't actually test this because webob does the wrong
        #thing when trying to decompress the body. Below is error and
        #webob code
        '''
        # Weird feature: http://bugs.python.org/issue5784
        self.body = zlib.decompress(self.body, -15)
        error: Error -3 while decompressing data: invalid stored block lengths
        '''

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        pass

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        pass


class GnomeMapTest(FunctionalTestBase):
    '''
        Tests out the Gnome Map object API
    '''
    req_data = {'obj_type': 'gnome.maps.map.GnomeMap',
                }
    fields_to_check = ('id', 'obj_type')

    def test_get_no_id(self):
        resp = self.testapp.get('/map')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/map/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create the object by performing a post
        # 2. get the valid id from the response
        # 3. perform an additional get of the object with a valid id
        # 4. check that our new JSON response matches the one from the create
        resp1 = self.testapp.post_json('/map', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/map/{0}'.format(obj_id))

        for k in self.fields_to_check:
            assert resp2.json_body[k] == resp1.json_body[k]

    def test_post_no_payload(self):
        self.testapp.post_json('/map', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/map', status=400)

    def test_put_no_id(self):
        self.testapp.put_json('/map', params=self.req_data,
                              status=404)

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/map', params=params,
                              status=404)

    def test_put_valid_id(self):
        # 1. create the object by performing a post
        # 2. get the valid id from the response
        # 3. update the properties in the JSON response
        # 4. update the object by performing a put with a valid id
        # 5. check that our new properties are in the new JSON response
        resp = self.testapp.post_json('/map', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/map', params=req_data)
        self.check_updates(resp.json_body)

    def perform_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        pass

    def check_updates(self, json_obj):
        '''
            We can overload this function when subclassing our tests
            for new object types.
        '''
        pass

"""
class MapGeoJsonTest(FunctionalTestBase):
    '''
        Tests out the Gnome Map object API
    '''
    req_data = {'obj_type': 'gnome.maps.map.MapFromBNA',
                'filename': 'Test.bna',
                'refloat_halflife': 1.0
                }

    def test_put_valid_id(self):
        self.setup_map_file()
        resp = self.testapp.post_json('/map', params=self.req_data)
        map1 = resp.json_body

        resp = self.testapp.get('/map/{0}/geojson'.format(map1['id']))
        geo_json = resp.json_body

        assert geo_json['type'] == 'FeatureCollection'
        assert 'features' in geo_json

        for f in geo_json['features']:
            assert 'type' in f
            assert 'geometry' in f
            assert 'coordinates' in f['geometry']
            for coord_coll in f['geometry']['coordinates']:
                assert len(coord_coll) == 1

                # This is the level where the individual coordinates are
                assert len(coord_coll[0]) > 1
                for c in coord_coll[0]:
                    assert len(c) == 2

    def test_all_goods_maps(self):
        req = self.req_data.copy()
        goods_url = 'https://gnome.orr.noaa.gov/goods/bnas'

        for map_file in ('newyork.bna',
                         'lakesuperior.bna',
                         'lakeontario.bna',
                         'lakehuron.bna',
                         'lakemichigan.bna'):
            req['filename'] = '/'.join([goods_url, map_file])
            print 'checking ', req['filename']

            resp = self.testapp.post_json('/map', params=req)
            map1 = resp.json_body

            # just some checks to see that we got our map
            assert len(map1['map_bounds']) == 4
            assert basename(map1['filename']) == map_file

            resp = self.testapp.get('/map/{0}/geojson'.format(map1['id']))
            geo_json = resp.json_body

            assert geo_json['type'] == 'FeatureCollection'
            assert 'features' in geo_json

            for f in geo_json['features']:
                assert 'type' in f
                assert 'geometry' in f
                assert 'properties' in f

                f_geo = f['geometry']
                assert 'coordinates' in f_geo

                if f_geo['type'] == 'MultiPolygon':
                    for coord_coll in f_geo['coordinates']:
                        assert len(coord_coll) == 1

                        # This is the level where the individual
                        # coordinates are
                        assert len(coord_coll[0]) > 1
                        for c in coord_coll[0]:
                            assert len(c) == 2
                elif f_geo['type'] == 'MultiLineString':
                    for coords in f_geo['coordinates']:
                        assert len(coords) > 1

                        # This is the level where the individual
                        # coordinates are
                        for c in coords:
                            assert len(c) == 2
                else:
                    assert False
"""

class ParamMapTest(FunctionalTestBase):
    '''
        Tests out the Gnome Map object API
    '''
    req_data = {'obj_type': 'gnome.maps.map.ParamMap',
                }

    def test_put_valid_id(self):
        self.setup_map_file()
        resp = self.testapp.post_json('/map', params=self.req_data)
        map1 = resp.json_body
        print map1

        resp = self.testapp.get('/map/{0}/geojson'.format(map1['id']))
        geo_json = resp.json_body

        assert geo_json['type'] == 'FeatureCollection'
        assert 'features' in geo_json

        for f in geo_json['features']:
            assert 'type' in f
            assert 'geometry' in f
            assert 'coordinates' in f['geometry']
            for coord_coll in f['geometry']['coordinates']:
                assert len(coord_coll) == 1

                # This is the level where the individual coordinates are
                assert len(coord_coll[0]) > 1
                for c in coord_coll[0]:
                    assert len(c) == 2
