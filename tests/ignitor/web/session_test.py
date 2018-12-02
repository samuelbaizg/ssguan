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

import time

from ssguan.ignitor.base.struct import Storage
from ssguan.ignitor.web import  config as web_config
from ssguan.ignitor.web.handler import BaseReqHandler, Rtn
from tests.ignitor.web.handler_test import WebTestCase


class SessionTest(WebTestCase):

    def get_handlers(self):
        class SessionReqHandler(BaseReqHandler):
            def get(self):
                rtn = Rtn()
                data = Storage()
                data.sid = self._session.sid
                rtn.set_data(data)
                rtn.write(self)

        class SessionDataHandler(BaseReqHandler):
            def get(self, *args, **kwargs):
                action = self.get_argument("action", 0)
                action = int(action)
                rtn = Rtn()
                data = Storage()
                data.sid = self._session.sid
                if action == 0:
                    self.session.tint = 1234
                    self.session.tstr = "1234addd"
                    self.session.tbool = False
                    self.session.tnone = "None"
                    self.session.tdelete = "tdelete"
                    self.session['eeeeaaaa'] = "eeeeaaaa"
                    data.tint = self._session.tint
                    data.tstr = self._session.tstr
                    data.tbool = self._session.tbool
                    data.tnone = self._session.tnone
                    data.tdelete = self._session.tdelete
                    data.eeeeaaaa = self._session['eeeeaaaa']
                elif action == 1:
                    data.tint = self._session.tint
                    data.tstr = self._session.tstr
                    data.tbool = self._session.tbool
                    data.tnone = self._session.tnone
                    data.tdelete = self._session.tdelete
                elif action == 2:
                    self._session.tint = 123433
                    self._session.tstr = "1234eeeeaaaddd"
                    self._session.tbool = True
                    self._session.tnone = None
                    self._session.tdict = {"a": 1, "b": "b"}
                    self._session.tlist = [1, 2, '3', 'a']
                    del self._session.tdelete
                elif action == 3:
                    data.tint = self._session.tint
                    data.tstr = self._session.tstr
                    data.tnone = self._session.tnone
                    data.tbool = self._session.tbool
                    data.tdict = self._session.tdict
                    data.tlist = self._session.tlist
                    if "tdelete" in self._session:
                        data.tdelete = self._session.tdelete
                    else:
                        data.tdelete = "truedeleted"
                elif action == 4:
                    pass

                rtn.set_data(data)
                rtn.write(self)

        class SessionTimeoutHandler(BaseReqHandler):
            def get(self, *args, **kwargs):
                rtn = Rtn()
                data = Storage()
                data.sid = self._session.sid

                action = self.get_argument("action", 0)
                action = int(action)
                if action == 0:
                    self._session.user = "testuser"
                    data.user = self._session.user
                elif action == 1:
                    if 'user' in self._session:
                        data.user = self._session.user
                    else:
                        data.user = "timeoutuser"
                elif action == 2:
                    pass
                rtn.set_data(data)
                rtn.write(self)

        return [("/session", SessionReqHandler),
                ("/sessiondata", SessionDataHandler),
                ("/sessiontimeout", SessionTimeoutHandler)
                ]

    def test_session(self):
        response = self.fetch("/session")
        headers = response.headers.get_list("Set-Cookie")
        body = self.get_response_body(response)
        sid = body.data['sid']
        self.assertEqual(response.code, 200)
        self.assertIn(web_config.get_sessionConfig().cookie_name, headers[0])
        headers = {"Cookie": headers[0]}
        response = self.fetch("/session", headers=headers)
        body = self.get_response_body(response)
        sid2 = body.data['sid']
        self.assertEqual(sid, sid2)
        response = self.fetch("/session")
        body = self.get_response_body(response)
        sid3 = body.data['sid']
        self.assertNotEqual(sid, sid3)

    def test_session_data(self):
        response = self.fetch("/sessiondata")
        self.assertEqual(response.code, 200)
        headers = response.headers.get_list("Set-Cookie")
        data = self.get_response_body(response).data
        self.assertEqual(data['tint'], 1234)
        self.assertEqual(data['tstr'], "1234addd")
        self.assertEqual(data['tbool'], False)
        self.assertEqual(data['tnone'], "None")
        self.assertEqual(data['tdelete'], "tdelete")
        self.assertEqual(data['eeeeaaaa'], "eeeeaaaa")
        headers = {"Cookie": headers[0]}
        response = self.fetch("/sessiondata?action=1", headers=headers)
        self.assertEqual(response.code, 200)
        data = self.get_response_body(response).data
        self.assertEqual(data['tint'], 1234)
        self.assertEqual(data['tstr'], "1234addd")
        self.assertEqual(data['tbool'], False)
        self.assertEqual(data['tnone'], "None")
        self.assertEqual(data['tdelete'], "tdelete")
        response = self.fetch("/sessiondata?action=2", headers=headers)
        response = self.fetch("/sessiondata?action=3", headers=headers)
        self.assertEqual(response.code, 200)
        data = self.get_response_body(response).data
        self.assertEqual(data['tint'], 123433)
        self.assertEqual(data['tstr'], "1234eeeeaaaddd")
        self.assertEqual(data['tbool'], True)
        self.assertEqual(data['tnone'], None)
        self.assertEqual(data['tdelete'], "truedeleted")
        self.assertEqual(data['tdict'], {"a": 1, "b": "b"})
        self.assertEqual(data['tlist'], [1, 2, '3', 'a'])
        response = self.fetch("/sessiondata?action=4")
        self.assertEqual(response.code, 200)
        data = self.get_response_body(response).data
        self.assertEqual(len(data), 1)
        self.assertNotIn("tint", data)
        self.assertIn("sid", data)
        response = self.fetch("/sessiondata?action=3", headers=headers)
        self.assertEqual(response.code, 200)
        data = self.get_response_body(response).data
        self.assertEqual(data['tint'], 123433)
        self.assertEqual(data['tstr'], "1234eeeeaaaddd")
        self.assertEqual(data['tbool'], True)
        self.assertEqual(data['tnone'], None)
        self.assertEqual(data['tdelete'], "truedeleted")
        self.assertEqual(data['tdict'], {"a": 1, "b": "b"})
        self.assertEqual(data['tlist'], [1, 2, '3', 'a'])

    def test_session_timeout(self):
        web_config.get_sessionConfig()._SessionConfig__timeout = 1
        response = self.fetch("/sessiontimeout")
        self.assertEqual(response.code, 200)
        headers = response.headers.get_list("Set-Cookie")
        headers = {"Cookie": headers[0]}
        data = self.get_response_body(response).data
        self.assertEqual(data['user'], "testuser")
        time.sleep(2)
        response = self.fetch("/sessiontimeout?action=1", headers=headers)
        self.assertEqual(response.code, 200)
        data = self.get_response_body(response).data
        self.assertEqual(data['user'], "timeoutuser")

        web_config.get_sessionConfig()._SessionConfig__timeout = 2
        response = self.fetch("/sessiontimeout")
        self.assertEqual(response.code, 200)
        headers = response.headers.get_list("Set-Cookie")
        headers = {"Cookie": headers[0]}
        time.sleep(1)
        response = self.fetch("/sessiontimeout?action=1", headers=headers)
        self.assertEqual(response.code, 200)
        data = self.get_response_body(response).data
        self.assertEqual(data['user'], "testuser")
        time.sleep(1)
        response = self.fetch("/sessiontimeout?action=1", headers=headers)
        self.assertEqual(response.code, 200)
        data = self.get_response_body(response).data
        self.assertEqual(data['user'], "testuser")
        time.sleep(3)
        response = self.fetch("/sessiontimeout?action=1", headers=headers)
        self.assertEqual(response.code, 200)
        data = self.get_response_body(response).data
        self.assertEqual(data['user'], "timeoutuser")
