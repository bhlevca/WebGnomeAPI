"""
Functional tests for the Gnome Map object Web API
"""
from os.path import basename
import pytest

from base import FunctionalTestBase


class MapTestBase(FunctionalTestBase):
    '''
        Tests out the Gnome Map object API
    '''
    req_data = {'obj_type': 'gnome.map.MapFromBNA',
                'filename': 'Test.bna',
                'refloat_halflife': 1.0
                }
    fields_to_check = ('id', 'obj_type', 'filename', 'refloat_halflife')

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
        req['filename'] = 'http://gnome.orr.noaa.gov/goods/bnas/galveston.bna'
        resp = self.testapp.post_json('/map', params=req)
        map1 = resp.json_body

        # just some checks to see that we got our map
        assert len(map1['map_bounds']) == 4
        assert basename(map1['filename']) == 'galveston.bna'

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
    req_data = {'obj_type': 'gnome.map.GnomeMap',
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


class MapGeoJsonTest(FunctionalTestBase):
    '''
        Tests out the Gnome Map object API
    '''
    req_data = {'obj_type': 'gnome.map.MapFromBNA',
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


class ParamMapTest(FunctionalTestBase):
    '''
        Tests out the Gnome Map object API
    '''
    req_data = {'obj_type': 'gnome.map.ParamMap',
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
