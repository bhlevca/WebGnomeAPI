"""
Functional tests for the Gnome Distribution object Web API
"""
from base import FunctionalTestBase


class DistributionBase(FunctionalTestBase):
    '''
        Tests out the Gnome Distribution object API
    '''
    req_data = {'obj_type': 'gnome.utilities.distributions.NormalDistribution',
                'json_': 'webapi',
                'mean': 0.0,
                'sigma': 0.1
                }
    fields_to_check = ('id', 'obj_type')

    def test_get_no_id(self):
        resp = self.testapp.get('/distribution')

        assert 'obj_type' in self.req_data
        obj_type = self.req_data['obj_type'].split('.')[-1]

        assert (obj_type, obj_type) in [(name, obj['obj_type'].split('.')[-1])
                                        for name, obj
                                        in resp.json_body.iteritems()]

    def test_get_invalid_id(self):
        obj_id = 0xdeadbeef
        self.testapp.get('/distribution/{0}'.format(obj_id), status=404)

    def test_get_valid_id(self):
        # 1. create the object by performing a post
        # 2. get the valid id from the response
        # 3. perform an additional get of the object with a valid id
        # 4. check that our new JSON response matches the one from the create
        resp1 = self.testapp.post_json('/distribution', params=self.req_data)

        obj_id = resp1.json_body['id']
        resp2 = self.testapp.get('/distribution/{0}'.format(obj_id))

        for k in self.fields_to_check:
            assert resp2.json_body[k] == resp1.json_body[k]

    def test_post_no_payload(self):
        self.testapp.post_json('/distribution', status=400)

    def test_put_no_payload(self):
        self.testapp.put_json('/distribution', status=400)

    def test_put_no_id(self):
        self.testapp.put_json('/distribution', params=self.req_data,
                              status=404)

    def test_put_invalid_id(self):
        params = {}
        params.update(self.req_data)
        params['id'] = str(0xdeadbeef)

        self.testapp.put_json('/distribution', params=params,
                              status=404)

    def test_put_valid_id(self):
        # 1. create the object by performing a post
        # 2. get the valid id from the response
        # 3. update the properties in the JSON response
        # 4. update the object by performing a put with a valid id
        # 5. check that our new properties are in the new JSON response
        resp = self.testapp.post_json('/distribution', params=self.req_data)

        req_data = resp.json_body
        self.perform_updates(req_data)

        resp = self.testapp.put_json('/distribution', params=req_data)
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


class UniformDistributionTests(DistributionBase):
    req_data = {'obj_type': 'gnome.utilities.distributions.UniformDistribution',
                'json_': 'webapi',
                'low': 0.0,
                'high': 0.1
                }
    fields_to_check = ('id', 'obj_type', 'low', 'high')

    def perform_updates(self, json_obj):
        super(UniformDistributionTests, self).perform_updates(json_obj)

        json_obj['low'] = 0.1
        json_obj['high'] = 0.2

    def check_updates(self, json_obj):
        super(UniformDistributionTests, self).check_updates(json_obj)

        assert json_obj['low'] == 0.1
        assert json_obj['high'] == 0.2


class NormalDistributionTests(DistributionBase):
    req_data = {'obj_type': 'gnome.utilities.distributions.NormalDistribution',
                'json_': 'webapi',
                'mean': 0.0,
                'sigma': 0.1
                }
    fields_to_check = ('id', 'obj_type', 'mean', 'sigma')

    def perform_updates(self, json_obj):
        super(NormalDistributionTests, self).perform_updates(json_obj)

        json_obj['mean'] = 0.1
        json_obj['sigma'] = 0.2

    def check_updates(self, json_obj):
        super(NormalDistributionTests, self).check_updates(json_obj)

        assert json_obj['mean'] == 0.1
        assert json_obj['sigma'] == 0.2


class LogNormalDistributionTests(DistributionBase):
    req_data = {'obj_type': 'gnome.utilities.distributions.LogNormalDistribution',
                'json_': 'webapi',
                'mean': 0.0,
                'sigma': 0.1
                }
    fields_to_check = ('id', 'obj_type', 'mean', 'sigma')

    def perform_updates(self, json_obj):
        super(LogNormalDistributionTests, self).perform_updates(json_obj)

        json_obj['mean'] = 0.1
        json_obj['sigma'] = 0.2

    def check_updates(self, json_obj):
        super(LogNormalDistributionTests, self).check_updates(json_obj)

        assert json_obj['mean'] == 0.1
        assert json_obj['sigma'] == 0.2


class WeibullDistributionTests(DistributionBase):
    req_data = {'obj_type': 'gnome.utilities.distributions.WeibullDistribution',
                'json_': 'webapi',
                'alpha': 0.0,
                'lambda_': 1.0,
                'min_': 0.1,
                'max_': 0.5,
                }
    fields_to_check = ('id', 'obj_type', 'alpha', 'lambda_', 'min_', 'max_')

    def perform_updates(self, json_obj):
        super(WeibullDistributionTests, self).perform_updates(json_obj)

        json_obj['alpha'] = 0.1
        json_obj['lambda_'] = 2.0
        json_obj['min_'] = 0.001
        json_obj['max_'] = 0.005

    def check_updates(self, json_obj):
        super(WeibullDistributionTests, self).check_updates(json_obj)

        assert json_obj['alpha'] == 0.1
        assert json_obj['lambda_'] == 2.0
        assert json_obj['min_'] == 0.001
        assert json_obj['max_'] == 0.005
