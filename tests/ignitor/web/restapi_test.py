# -*- coding: utf-8 -*-

#  Copyright 2015 www.suishouguan.com
#
#  Licensed under the Private License (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from ssguan.ignitor.auth import service as auth_service
from ssguan.ignitor.auth.model import Role
from ssguan.ignitor.orm import properti
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.utility import crypt, kind
from ssguan.ignitor.web import  config as web_config
from ssguan.ignitor.web.handler import Rtn
from ssguan.ignitor.web.restapi import FuncReqHandler, AuthReqHandler
from tests.ignitor.web.handler_test import WebTestCase, req_rtn


class AuthReqHandlerTest(WebTestCase):

    def get_handlers(self):

        class CurrentUserHandler(AuthReqHandler):
            @req_rtn()
            def get(self, *args, **kwargs):
                r = {}
                token = self.get_current_user()
                r['token'] = token
                r['pid'] = self.session.sid
                return r

        return [
            ("/cur", CurrentUserHandler),
            
        ]

    def test_prepare(self):
        web_config.get_sessionConfig()._SessionConfig__timeout = 180
        response1 = self.fetch("/cur")
        body1 = self.get_response_body(response1).data
        self.assertEqual(body1['token']['anonymous'], True)
        headers = response1.headers.get_list("Set-Cookie")
        headers = {"Cookie": headers[0]}
        response2 = self.fetch("/cur", headers=headers)
        body2 = self.get_response_body(response2).data
        self.assertEqual(body1['pid'], body2['pid'])
        lopuKey1 = body1['token']['lopuKey']
        lopuKey2 = body2['token']['lopuKey']
        self.assertEqual(lopuKey1, lopuKey2)

def api_a():
    return "empty arguments"

def api_b(a, b, c='ff', d=None):
    return "arguments %s %s %s %s" % (str(a), str(b), str(c), str(d))

def api_c(a, **kwargs):
    return "support kwargs %s b=%s c=%s" % (str(a), kwargs['b'], kwargs['c'])

class TModelWeb(Model):
    @classmethod
    def meta_domain(cls):
        return "test"
    f_str = properti.StringProperty(length=40)
    f_int = properti.IntegerProperty()
    f_date = properti.DateProperty()
    f_datetime = properti.DateTimeProperty()
    f_float = properti.FloatProperty()
    
class RestReqTest(WebTestCase):
    
    @classmethod
    def setUpClass(cls):
        super(RestReqTest, cls).setUpClass()
        role = auth_service.get_role(role_id=Role.ID_ANONYMOUS)
        role.create_roleoperation('per1')
        TModelWeb.create_schema()
    
    def get_handlers(self):
        return [("/api/fn/(.*)", FuncReqHandler)                
                ]
        
    def test_noargs(self):
        response = self.fetch("/api/fn/noargs")
        self.assertEqual(response.code, 200)
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "empty arguments")
    
    def test_queryargs(self):
        response = self.fetch("/api/fn/args_get?" + self.to_args({'a':123, 'b':456, 'c':'gg'}))
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "arguments 123 456 gg None")
        response = self.fetch("/api/fn/args_get?" + self.to_args({'a':123, 'b':456}))
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "arguments 123 456 ff None")
        response = self.fetch("/api/fn/args_delete?" + self.to_args({'a':123, 'b':456, 'd':'gaf'}), method='DELETE')
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "arguments 123 456 ff gaf")
    
    def test_bodyargs(self):
        response = self.fetch("/api/fn/args_post", method="POST", body=self.to_args({'a':123, 'b':456, 'c':'gg'}))
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "arguments 123 456 gg None")
        response = self.fetch("/api/fn/args_put" , method="PUT", body=self.to_args({'a':123, 'b':456}))
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "arguments 123 456 ff None")
        response = self.fetch("/api/fn/args_put" , method="PUT", body=self.to_args({'a':123, 'b':456, 'c':789, 'd':1012}))
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "arguments 123 456 789 1012")
    
    def test_kwargs(self):
        response = self.fetch("/api/fn/kwargs?" + self.to_args({'a':123, 'b':456, 'c':'gg'}))
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "support kwargs 123 b=456 c=gg")
        response = self.fetch("/api/fn/kwargs?" + self.to_args({ 'b':456, 'c':'gg'}))
        body = self.get_response_body(response)
        self.assertEqual(body.status, 200)
        self.assertEqual(body.data, "support kwargs None b=456 c=gg")
    
    def test_get_model(self):
        key = TModelWeb(f_str="f_str0").create(1).key()
        response = self.fetch("/api/fn/gettm")
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        response = self.fetch("/api/fn/gettm?%s" % (self.to_args({"key": key})))
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        self.assertEqual(body.data['key'], key)
    
    def test_fetch_models(self):
        query = TModelWeb.all()
        query.delete(None)
        TModelWeb(f_str="fStr0").create(1)
        TModelWeb(f_str="fStr0", f_int=12222).create(1)
        response = self.fetch("/api/fn/fetchtm?%s" % (self.to_args(
            {"filters": {"propertyOp": "f_str =", "value": "fStr0"}})))
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        self.assertEqual(len(body.data), 2)
        self.assertEqual(body.data[0]['f_str'], "fStr0")
        response = self.fetch("/api/fn/fetchtm?%s" % (self.to_args({"filters": {
                              "propertyOp": "f_str =", "value": "fStr0", "xcca": "yqq3"}})))
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        self.assertEqual(len(body.data), 2)
        response = self.fetch("/api/fn/fetchtm?%s" % (self.to_args(
            {"filters": {"cae": "f_str =", "value": "fStr0"}})))
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        response = self.fetch("/api/fn/fetchtm?%s" % (self.to_args(
            {"filters": {"propertyOp": "f_str =", "value1": "fStr0"}})))
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        response = self.fetch("/api/fn/fetchtm?%s" % (self.to_args({"filters": {
            "propertyOp": "f_str =", "value": "fStr0", "xcca": "yqq3"}, "whats": ["f_int"]})))
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        response = self.fetch("/api/fn/fetchtm?%s" % (self.to_args({"filters": {
            "propertyOp": "f_str =", "value": "fStr0", "xcca": "yqq3"}, "whats": ["f_date1"]})))
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        response = self.fetch("/api/fn/fetchtm?%s" % (self.to_args({"filters": {
            "propertyOp": "f_str =", "value": "fStr0", "xcca": "yqq3"}, "whats": ["f_int"], "orders": "-f_str"})))
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)

    def test_create_model(self):
        args = {'f_str': 'f_str111', 'f_int': 101, 'f_float': 1.2,
                'f_date': "2015-03-03", 'f_datetime': '2015-02-04 02:03'}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch("/api/fn/createtm" , body=args, method="POST")
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['f_datetime'], '2015-02-04 02:03:00')
        self.assertEqual(body['f_date'], '2015-03-03')
        self.assertEqual(body['f_float'], 1.2)
        self.assertEqual(body['f_int'], 101)
        self.assertEqual(body['f_str'], 'f_str111')
        args = {'f_str': 'f_str111f_str111f_str111f_str111f_str111f_strf_str111fstf_str111f_str111f_str111f_str111f_str111f_strr111f_str111f_str111f_str111f_str',
                'f_int': 23232323, 'f_float': 232323233.2, 'f_date': "2015/06/03", 'f_dateFMT': '%Y/%m/%d', 'f_datetime': '201508-04 02', 'f_datetimeFMT': '%Y%m-%d %H'}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "/api/fn/createtm" , body=args, method="POST")
        body = self.get_response_body(response)
        self.assertEqual(1012, body.status)
        args = {'f_str': 'fffadfdasfsdaf', 'f_int': 11111123, 'f_float': 232323233.2, 'f_date': "2015/06/03",
                'f_dateFMT': '%Y/%m/%d', 'f_datetime': '201508-04 02', 'f_datetimeFMT': '%Y%m-%d %H'}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "/api/fn/createtm", body=args, method="POST")
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['f_datetime'], '2015-08-04 02:00:00')
        self.assertEqual(body['f_date'], '2015-06-03')
        self.assertEqual(body['f_float'], 232323233.2)
        self.assertEqual(body['f_int'], 11111123)
        self.assertEqual(body['f_str'], 'fffadfdasfsdaf')
        args = {'f_str': 'f_str111', 'f_int': 101,
                'f_float': 1.2, 'key': '33323222'}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "/api/fn/createtm" , body=args, method="POST")
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['key'], '33323222')

    def test_update_model(self):
        args = {'f_str': 'f_str111', 'f_int': 101, 'f_float': 1.2,
                'f_date': "2015-03-03", 'f_datetime': '2015-02-04 02:03'}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "/api/fn/updatetm", body=args, method="PUT")
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        args = {'key': '2233', 'f_str': 'f_str111', 'f_int': 101, 'f_float': 1.2,
                'f_date': "2015-03-03", 'f_datetime': '2015-02-04 02:03'}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "/api/fn/updatetm" , body=args, method="PUT")
        body = self.get_response_body(response)
        self.assertEqual(1004, body.status)
        tmodel = TModelWeb(f_str="aa", f_int=12, f_float=3223.0)
        tmodel.create("222")
        args = {'key': tmodel.key(), 'f_str': 'f_str111', 'f_int': 223, 'f_float': 122.2,
                'f_date': "2015-03-23", 'f_datetime': '2015-03-22 12:03'}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "/api/fn/updatetm", body=args, method="PUT")
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['f_datetime'], '2015-03-22 12:03:00')
        self.assertEqual(body['f_date'], '2015-03-23')
        self.assertEqual(body['f_float'], 122.2)
        self.assertEqual(body['f_int'], 223)
        self.assertEqual(body['f_str'], 'f_str111')
        args = {'key': tmodel.key(), 'f_str': 'adeddadsfasdfadfsasdfasdf', 'f_int': 222333, 'f_float': 13322.2,
                'f_date': "2012-1123", 'f_dateFMT': '%Y-%m%d', 'f_datetime': '20160322 11:03:55', 'f_datetimeFMT': '%Y%m%d %H:%M:%S'}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "/api/fn/updatetm" , body=args, method="PUT")
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['f_datetime'], '2016-03-22 11:03:55')
        self.assertEqual(body['f_date'], '2012-11-23')
        self.assertEqual(body['f_float'], 13322.2)
        self.assertEqual(body['f_int'], 222333)
        self.assertEqual(body['f_str'], 'adeddadsfasdfadfsasdfasdf')

    def test_delete_model(self):
        tmodel = TModelWeb(f_str="a222a", f_int=12, f_float=3223.0)
        tmodel.create("222")
        args = {'key1': tmodel.key()}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch("/api/fn/deletetm?%s" % (
                                                    args), method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        args = {'key': tmodel.key()}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch("/api/fn/deletetm?%s" % 
                              (args), method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        tmodel = TModelWeb(f_str="a2cc22a", f_int=12, f_float=3223.0)
        key1 = tmodel.create("222").key()
        tmodel = TModelWeb(f_str="accc2cc22a", f_int=12, f_float=3223.0)
        key2 = tmodel.create("222").key()
        args = {'keys': [key1, key2]}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch("/api/fn/deletetm?%s" % 
                              (args), method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)

