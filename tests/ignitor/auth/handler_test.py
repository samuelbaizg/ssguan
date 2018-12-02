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
from ssguan.ignitor.auth.handler import LogoutHandler, LoginHandler
from ssguan.ignitor.auth.model import User
from ssguan.ignitor.base import error, context
from ssguan.ignitor.utility import crypt, kind
from ssguan.ignitor.web.decorator import req_rtn
from ssguan.ignitor.web.handler import Rtn
from ssguan.ignitor.web.restapi import AuthReqHandler
from tests.ignitor.web.handler_test import WebTestCase


def set_token():
    token = auth_service.login(None, None, True)
    context.set_token(token)
    return token

class PrepareReqHandler(AuthReqHandler):
    
    @req_rtn()
    def get(self):
        token = self.get_current_user()
        return token

class LoginHandlerTest(WebTestCase):
       
    def login(self, loginName, password, lopuKey, headers):
        loginName = crypt.rsa_encrypt(loginName, lopuKey)
        password = crypt.rsa_encrypt(password, lopuKey)
        args = {"loginName": loginName, "loginPassword": password}
        args = crypt.str_to_base64(
            kind.obj_to_json(args), remove_cr=True)
        response = self.fetch("/login", method="POST", body=args, headers=headers)
        return response

    def login_superadmin(self):
        (lopuKey, headers) = self.get_lopukey_and_headers()
        self.login(User.ACCOUNT_NAME_ROOT,
                   User.ACCOUNT_NAME_ROOT, lopuKey, headers)
        headers = self.get_lopukey_and_headers(headers=headers)[1]
        return headers
    
    def get_lopukey_and_headers(self, headers=None):
        response = self.fetch("/prepare", headers=headers)
        body = self.get_response_body(response).data
        headers = response.headers.get_list("Set-Cookie")
        headers = {"Cookie": headers[0]}
        return (body['lopuKey'], headers)

    def get_handlers(self):
        handlers = []
        handlers.append(("/prepare", PrepareReqHandler))
        handlers.append(("/login", LoginHandler))
        handlers.append(("/logout", LogoutHandler))
        return handlers

    def test_login(self):
        set_token()
        auth_service.create_user("test11", "password11", False)
        args = {"loginName": "test1", "loginPassword": ""}
        response = self.fetch("/login" , method="POST",
                              body=kind.obj_to_json(args))
        body = self.get_response_body(response)
        self.assertEqual(error.CODE_UNKNOWN, body['status'])
        self.assertEqual("Incorrect padding", body['message'])
        lopuKey = self.get_lopukey_and_headers()[0]
        response = self.login("test11", "password11", lopuKey, None)
        body = self.get_response_body(response)
        self.assertEqual("Decryption failed", body['message'])
        (lopuKey, headers) = self.get_lopukey_and_headers()
        response = self.login("test11", "password11", lopuKey, headers)
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['anonymous'], False)
        self.assertEqual(body['account'], "test11")
        response = self.fetch("/prepare", headers=headers)
        body1 = self.get_response_body(response).data
        self.assertEqual(body1['anonymous'], False)
        self.assertEqual(body1['account'], "test11")

    def test_logout(self):
        set_token()
        auth_service.create_user("test12", "password12", False)
        (lopuKey, headers) = self.get_lopukey_and_headers()
        response = self.login("test12", "password12", lopuKey, headers)
        body = self.get_response_body(response)
        self.assertEqual(Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['anonymous'], False)
        self.assertEqual(body['account'], "test12")
        response = self.fetch("/logout", method="POST",
                              body=crypt.str_to_base64("{}", True), headers=headers)
        body = self.get_response_body(response).data
        self.assertEqual(body['anonymous'], True)
        self.assertEqual(body['account'], 'anonymous')
        response = self.fetch("/prepare", headers=headers)
        body1 = self.get_response_body(response).data
        self.assertEqual(body1['anonymous'], True)

