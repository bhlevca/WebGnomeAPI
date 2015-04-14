"""
Functional tests for the Gnome ElementType object Web API
"""
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

from base import FunctionalTestBase


class ElementTypeBase(FunctionalTestBase):
    '''
        Tests out the Gnome ElementType object API
    '''
    init_data = {'obj_type': u'gnome.spill.elements.InitWindages',
                 'windage_range': (0.01, 0.04),
                 'windage_persist': 900,
                 }

    req_data = {'obj_type': u'gnome.spill.elements.ElementType',
                'initializers': None,
                'substance': u'ALASKA NORTH SLOPE (MIDDLE PIPELINE)'
                }

    fields_to_check = ('id', 'obj_type', 'initializers')

    def test_get_no_id(self):
        resp = self.testapp.get('/element_type')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/element_type/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create the object by performing a put with no id
        # 2. get the valid id from the response
        # 3. perform an additional get of the object with a valid id
        # 4. check that our new JSON response matches the one from the create
        self.req_data['initializers'] = self.create_init_obj(self.init_data)
        resp1 = self.testapp.post_json('/element_type', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/element_type/{0}'.format(obj_id))

        for k in self.fields_to_check:
            assert resp2.json_body[k] == resp1.json_body[k]

    def test_post_no_payload(self):
        self.testapp.post_json('/element_type', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/element_type', status=400)

    def test_put_no_id(self):
        self.req_data['initializers'] = self.create_init_obj(self.init_data)
        self.testapp.put_json('/element_type', params=self.req_data,
                              status=404)

    def test_put_invalid_id(self):
        self.req_data['initializers'] = self.create_init_obj(self.init_data)
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/element_type', params=params, status=404)

    def test_put_valid_id(self):
        self.req_data['initializers'] = self.create_init_obj(self.init_data)
        print 'req_data:'
        pp.pprint(self.req_data)
        resp = self.testapp.post_json('/element_type', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/element_type', params=req_data)
        self.check_updates(resp.json_body)

    def create_init_obj(self, req_data):
        resp = self.testapp.post_json('/initializer', params=req_data)
        return [resp.json_body]

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


class ElementTypeWithWindagesTests(ElementTypeBase):
    pass


class ElementTypeWithRiseVelDistTest(ElementTypeBase):
    dist_data = {'obj_type': ('gnome.utilities.distributions'
                              '.WeibullDistribution'),
                 'alpha': 0.0,
                 'lambda_': 1.0,
                 'min_': 0.1,
                 'max_': 0.5,
                 }
    init_data = {'obj_type': u'gnome.spill.elements.InitRiseVelFromDist',
                 'distribution': None
                 }
    fields_to_check = ('id', 'obj_type', 'initializers')

    def create_dist_obj(self, req_data):
        resp = self.testapp.post_json('/distribution', params=req_data)
        return resp.json_body

    def create_init_obj(self, req_data, dist_obj=None):
        if dist_obj:
            req_data['distribution'] = dist_obj
        resp = self.testapp.post_json('/initializer', params=req_data)
        return [resp.json_body]

    def test_get_valid_id(self):
        dist_obj = self.create_dist_obj(self.dist_data)
        init_obj = self.create_init_obj(self.init_data, dist_obj)
        self.req_data['initializers'] = init_obj
        resp1 = self.testapp.post_json('/element_type', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/element_type/{0}'.format(obj_id))

        for k in self.fields_to_check:
            assert resp2.json_body[k] == resp1.json_body[k]

    def test_put_no_id(self):
        dist_obj = self.create_dist_obj(self.dist_data)
        init_obj = self.create_init_obj(self.init_data, dist_obj)
        self.req_data['initializers'] = init_obj

        self.testapp.put_json('/element_type', params=self.req_data,
                              status=404)

    def test_put_invalid_id(self):
        dist_obj = self.create_dist_obj(self.dist_data)
        init_obj = self.create_init_obj(self.init_data, dist_obj)
        self.req_data['initializers'] = init_obj
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/element_type', params=params, status=404)

    def test_put_valid_id(self):
        dist_obj = self.create_dist_obj(self.dist_data)
        init_obj = self.create_init_obj(self.init_data, dist_obj)
        self.req_data['initializers'] = init_obj

        resp = self.testapp.post_json('/element_type', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/element_type', params=req_data)
        self.check_updates(resp.json_body)

    def perform_updates(self, json_obj):
        super(ElementTypeWithRiseVelDistTest, self).perform_updates(json_obj)
        # there is nothing to update directly inside this object

    def check_updates(self, json_obj):
        super(ElementTypeWithRiseVelDistTest, self).check_updates(json_obj)
        # there is nothing to check directly inside this object
