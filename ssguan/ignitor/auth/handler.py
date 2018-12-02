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

from ssguan.ignitor.auth.model import User
from ssguan.ignitor.auth.service import login, logout
from ssguan.ignitor.base.error import RequiredError
from ssguan.ignitor.utility import kind
from ssguan.ignitor.web.decorator import req_rtn
from ssguan.ignitor.web.restapi import AuthReqHandler


class LoginHandler(AuthReqHandler):
    
    @req_rtn()
    def post(self, *args, **kwargs):
        body = self.decode_arguments_body()
        login_name = body['loginName']
        if login_name == User.ACCOUNT_NAME_ANONYMOUS:
            token = self.get_current_user()
            if token is None:
                token = login(None, None, is_anonymous=True)            
        else:
            if kind.str_is_empty(login_name):
                raise RequiredError("loginName")
            if kind.str_is_empty(login_name):
                raise RequiredError("loginPassword")            
            login_password = body['loginPassword']
            token = login(login_name, login_password)
        self.set_current_user(token)
        return token

class LogoutHandler(AuthReqHandler):
    
    @req_rtn()    
    def post(self, *args, **kwargs):
        token = logout()        
        self.set_current_user(token)
        return token
