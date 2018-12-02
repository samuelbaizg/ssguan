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

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from ssguan.ignitor.base.error import Error, CODE_UNKNOWN
from ssguan.ignitor.base.struct import Storage
from ssguan.ignitor.orm import dbpool, config as orm_config, update
from ssguan.ignitor.utility import crypt, kind
from ssguan.ignitor.web import config as web_config
from ssguan.ignitor.web.decorator import req_rtn
from ssguan.ignitor.web.handler import BaseReqHandler, Rtn


class WebTestCase(AsyncHTTPTestCase):
    """Base class for webb tests that also supports WSGI mode.

    Override get_handlers and get_app_kwargs instead of get_app.
    Append to wsgi_safe to have it run in wsgi_test as well.
    """
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        update.install()
        update.upgrade()

    def get_app(self):
        self.app = Application(self.get_handlers(), **self.get_app_kwargs())
        return self.app

    def get_handlers(self):
        raise NotImplementedError("WebTestCase.get_handlers")

    def get_app_kwargs(self):
        return {"cookie_secret": web_config.get_sessionConfig().secret_key,
                "default_handler_class": web_config.get_settings()["default_handler_class"]}

    def get_response_body(self, response, json=True):
        body = crypt.base64_to_str(response.body)
        if json:
            jsonobj = kind.json_to_object(body)
            return Storage(**jsonobj) if jsonobj != None else None
        else:
            return body

    def to_args(self, kwargs):
        args = kind.obj_to_json(kwargs)
        args = crypt.str_to_base64(args, remove_cr=True)
        return args
    
    @classmethod
    def tearDownClass(cls):
        dbpool.drop_db(orm_config.get_default_dbinfo())


class BError(Error):
    def __init__(self, message):
        super(BError, self).__init__(message)

    @property
    def code(self):
        return 3000


class BaseReqHandlerTest(WebTestCase):

    def get_handlers(self):
        class ErrorReqHandler(BaseReqHandler):

            def get(self, *args, **kwargs):
                raise BError("known")

            def post(self, *args, **kwargs):
                raise Exception("unknown")

        class RtnReqHandler(BaseReqHandler):

            def get(self, *args, **kwargs):
                rtn = Rtn(data="rtntest")
                rtn.write(self)
                
        class RtnTextHandler(BaseReqHandler):

            def get(self, *args, **kwargs):
                ch = self.get_argument("ch")
                rtn = Rtn(content_type="text/html", data=ch)
                rtn.write(self)
        
        class DecArgReqHandler(BaseReqHandler):

            @req_rtn()
            def get(self, *args, **kwargs):
                args1 = self.decode_arguments_query()
                return args1 if len(args1) > 0 else {"zero": True}

            @req_rtn()
            def post(self, *args, **kwargs):
                argsuri = self.decode_arguments_query()
                argsbody = self.decode_arguments_body()
                if len(argsuri) == 0 and len(argsbody) == 0:
                    return {"zero11": True}
                else:
                    return kind.dict_add(argsuri, argsbody)

            @req_rtn()
            def put(self, *args, **kwargs):
                argsuri = self.decode_arguments_query()
                argsbody = self.decode_arguments_body()
                if len(argsuri) == 0 and len(argsbody) == 0:
                    return {"zero22": True}
                else:
                    return kind.dict_add(argsuri, argsbody)

            @req_rtn()
            def delete(self, *args, **kwargs):
                argsuri = self.decode_arguments_query()
                if len(argsuri) == 0:
                    return {"zero33": True}
                else:
                    return argsuri

        return [("/error", ErrorReqHandler),
                ("/rtn", RtnReqHandler),
                ("/rtntext", RtnTextHandler),
                ("/decarg", DecArgReqHandler),
            ("/decarg/([^/]+)", DecArgReqHandler),
                ]

    def test_write_error(self):
        response = self.fetch("/error")        
        self.assertEqual(200, response.code)
        body = self.get_response_body(response)
        self.assertEqual(3000, body.status)
        self.assertEqual("", body.data)
        self.assertEqual("3000: known", body.message)
        self.assertEqual({}, body.arguments)
        self.assertEqual(len(body), 4)
        response = self.fetch("/error", method="POST", body="foo=bar")
        self.assertEqual(200, response.code)
        body = self.get_response_body(response)
        self.assertEqual(CODE_UNKNOWN, body.status)
        self.assertEqual("", body.data)
        self.assertEqual("unknown", body.message)
        self.assertEqual({}, body.arguments)
        self.assertEqual(len(body), 4)
        response = self.fetch("/error", method="PUT", body="foo=bar")
        self.assertEqual(200, response.code)
        body = self.get_response_body(response)
        self.assertEqual(CODE_UNKNOWN, body.status)
        self.assertEqual(len(body), 4)

    def test_rtn(self):
        response = self.fetch("/rtn")
        self.assertEqual(200, response.code)
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        self.assertEqual("rtntest", body.data)
        
    def test_rtntext(self):
        response = self.fetch("/rtntext?ch=rtntext")
        self.assertEqual(200, response.code)
        self.assertEqual(kind.safestr(response.body), "rtntext")
        response = self.fetch(u"/rtntext?ch=abcdef")
        self.assertEqual(200, response.code)
        self.assertEqual(kind.safestr(response.body), "abcdef")
        
    def test_decode_arguments_query(self):
        args = kind.obj_to_json({"a": False, "c": "cstring"})
        args = crypt.str_to_base64(args, remove_cr=True)
        response = self.fetch("/decarg/mm?%s" % args)
        self.assertEqual(200, response.code)
        body = self.get_response_body(response)
        self.assertEqual(body.data['a'], False)
        self.assertEqual(body.data['c'], "cstring")
        response = self.fetch("/decarg/gg")
        body = self.get_response_body(response)
        self.assertEqual(body.data['zero'], True)

    def test_decode_arguments_body(self):
        argsuri = kind.obj_to_json({"a11": True, "c11": "cstring12"})
        argsuri = crypt.str_to_base64(argsuri, remove_cr=True)
        argsbody = kind.obj_to_json({"a1": False, "c1": "cstring"})
        argsbody = crypt.str_to_base64(argsbody, remove_cr=True)
        response = self.fetch("/decarg?%s" % 
                              argsuri, method="POST", body=argsbody)
        body = self.get_response_body(response)
        self.assertEqual(body.data['a1'], False)
        self.assertEqual(body.data['c1'], "cstring")
        self.assertEqual(body.data['a11'], True)
        self.assertEqual(body.data['c11'], "cstring12")
        args = crypt.str_to_base64("", remove_cr=True)
        response = self.fetch("/decarg?", method="POST", body=args)
        body = self.get_response_body(response)
        self.assertEqual(body.data['zero11'], True)

        argsuri = kind.obj_to_json({"a21": True, "c21": "cstring22"})
        argsuri = crypt.str_to_base64(argsuri, remove_cr=True)
        argsbody = kind.obj_to_json({"a2": False, "c2": "cstring"})
        argsbody = crypt.str_to_base64(argsbody, remove_cr=True)
        response = self.fetch("/decarg?%s" % 
                              argsuri, method="PUT", body=argsbody)
        body = self.get_response_body(response)
        self.assertEqual(body.data['a21'], True)
        self.assertEqual(body.data['c21'], "cstring22")
        self.assertEqual(body.data['a2'], False)
        self.assertEqual(body.data['c2'], "cstring")
        args = crypt.str_to_base64("", remove_cr=True)
        response = self.fetch("/decarg?", method="PUT", body=args)
        body = self.get_response_body(response)
        self.assertEqual(body.data['zero22'], True)

        argsuri = kind.obj_to_json({"a3": False, "c3": "cstring"})
        argsuri = crypt.str_to_base64(argsuri, remove_cr=True)
        response = self.fetch("/decarg?%s" % argsuri, method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(body.data['a3'], False)
        self.assertEqual(body.data['c3'], "cstring")

        args = crypt.str_to_base64("", remove_cr=True)
        response = self.fetch("/decarg", method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(body.data['zero33'], True)
