"""
Functional tests for the Gnome Spill object Web API
"""
import pprint
pp = pprint.PrettyPrinter(indent=2)

from base import FunctionalTestBase


class SpillTests(FunctionalTestBase):
    '''
        Tests out the Gnome Spill object API
        TODO: Why is the element_type argument optional in Spill.__init__(),
              but required in Spill.new_from_dict()???  This does not seem
              like a consistent design.
    '''
    rel_req_data = {'obj_type': u'gnome.spill.release.PointLineRelease',
                    'num_elements': 100,
                    'num_released': 0,
                    'release_time': '2014-04-15T13:22:20.930570',
                    'start_time_invalid': True,
                    'end_release_time': '2014-04-15T13:22:20.930570',
                    'end_position': (28.0, -78.0, 0.0),
                    'start_position': (28.0, -78.0, 0.0),
                    }

    init_req_data = {'obj_type': u'gnome.spill.elements.InitWindages',
                     'windage_range': (0.01, 0.04),
                     'windage_persist': 900,
                     }
    elem_type_req_data = {'obj_type': u'gnome.spill.elements.ElementType',
                          'initializers': None,
                          }

    req_data = {'obj_type': u'gnome.spill.spill.Spill',
                'release': None,
                'element_type': None
                }
    fields_to_check = ('id', 'obj_type', 'release', 'element_type')

    def create_release_obj(self, req_data):
        resp = self.testapp.post_json('/release', params=req_data)
        return resp.json_body

    def create_init_obj(self, req_data):
        resp = self.testapp.post_json('/initializer', params=req_data)
        return {'windages': resp.json_body}

    def create_elem_type_obj(self, req_data, init_obj):
        req_data['initializers'] = init_obj
        resp = self.testapp.post_json('/element_type', params=req_data)
        return resp.json_body

    def test_get_no_id(self):
        resp = self.testapp.get('/spill')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/spill/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create a Release object
        # 2. create an ElementType object
        # 3. create a Spill object
        # 4. get the valid id from the Spill response
        # 5. perform an additional get of the object with a valid id
        # 6. check that our new JSON response matches the one from the create
        rel_obj = self.create_release_obj(self.rel_req_data)

        init_obj = self.create_init_obj(self.init_req_data)
        elem_type_obj = self.create_elem_type_obj(self.elem_type_req_data,
                                                  init_obj)
        self.req_data['release'] = rel_obj
        self.req_data['element_type'] = elem_type_obj

        resp1 = self.testapp.post_json('/spill', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/spill/{0}'.format(obj_id))

        for k in self.fields_to_check:
            assert resp2.json_body[k] == resp1.json_body[k]

    def test_post_no_payload(self):
        self.testapp.post_json('/spill', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/spill', status=400)

    def test_put_no_id(self):
        rel_obj = self.create_release_obj(self.rel_req_data)
        init_obj = self.create_init_obj(self.init_req_data)
        elem_type_obj = self.create_elem_type_obj(self.elem_type_req_data,
                                                  init_obj)
        self.req_data['release'] = rel_obj
        self.req_data['element_type'] = elem_type_obj

        self.testapp.put_json('/spill', params=self.req_data, status=404)

    def test_put_invalid_id(self):
        rel_obj = self.create_release_obj(self.rel_req_data)

        init_obj = self.create_init_obj(self.init_req_data)
        elem_type_obj = self.create_elem_type_obj(self.elem_type_req_data,
                                                  init_obj)
        self.req_data['release'] = rel_obj
        self.req_data['element_type'] = elem_type_obj

        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)
        self.testapp.put_json('/spill', params=params, status=404)

    def test_put_valid_id(self):
        rel_obj = self.create_release_obj(self.rel_req_data)

        init_obj = self.create_init_obj(self.init_req_data)
        elem_type_obj = self.create_elem_type_obj(self.elem_type_req_data,
                                                  init_obj)
        self.req_data['release'] = rel_obj
        self.req_data['element_type'] = elem_type_obj

        resp = self.testapp.post_json('/spill', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/spill', params=req_data)
        self.check_updates(resp.json_body)

    def perform_updates(self, json_obj):
        '''
            The Spill object is pretty much just a container for the Release
            and ElementType objects, and has no direct data properties
            that we can really tweak.
        '''

    def check_updates(self, json_obj):
        '''
            The Spill object is pretty much just a container for the Release
            and ElementType objects, and has no direct data properties
            that we can really tweak.
        '''


class SpillNestedTests(FunctionalTestBase):
    '''
        Tests out the nested object creation for the Gnome Spill object API
    '''
    req_data = {"obj_type": "gnome.spill.spill.Spill",
                "on": True,
                "release": {"obj_type": "gnome.spill.release.PointLineRelease",
                            "num_elements": 1000,
                            "num_released": 84,
                            "release_time": "2013-02-13T09:00:00",
                            "end_release_time": "2013-02-13T15:00:00",
                            "start_time_invalid": False,
                            "end_position": [144.664166, 13.441944, 0.0],
                            "start_position": [144.664166, 13.441944, 0.0],
                            },
                "element_type": {"obj_type": "gnome.spill.elements.ElementType",
                                 "initializers": {"windages": {"obj_type": "gnome.spill.elements.InitWindages",
                                                               "windage_range": [0.01, 0.04],
                                                               "windage_persist": 900,
                                                               }
                                                  }
                                 },
                }

    def test_get_valid_id(self):
        resp1 = self.testapp.post_json('/spill', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/spill/{0}'.format(obj_id))

        #print
        #pp.pprint(resp2.json_body)

        spill_body = resp2.json_body
        assert 'id' in spill_body
        assert 'id' in spill_body['release']
        assert 'id' in spill_body['element_type']
        assert 'id' in spill_body['element_type']['initializers']['windages']

        obj_id = spill_body['release']['id']
        resp2 = self.testapp.get('/release/{0}'.format(obj_id))
        assert 'id' in resp2.json_body

        obj_id = spill_body['element_type']['id']
        resp2 = self.testapp.get('/element_type/{0}'.format(obj_id))
        assert 'id' in resp2.json_body

        obj_id = spill_body['element_type']['initializers']['windages']['id']
        resp2 = self.testapp.get('/initializer/{0}'.format(obj_id))
        assert 'id' in resp2.json_body
