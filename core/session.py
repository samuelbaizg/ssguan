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
import conf
from core.model import stdModel
import web
import rsa
from core import cryptoutil

TOKEN_NAME = "SESSION_TOKEN"

class Token(stdModel):
    
    def __init__(self, user_id, anonymous=False, **props):
        super(stdModel, self).__init__(**props)
        self.user_id = user_id
        self.anonymous = anonymous
        self.rsa_key = cryptoutil.rsa_gen_key_hex(256)
    
    def is_anonymous(self):
        return self.anonymous is True
    
       
    def to_dict(self):
        dic = stdModel.to_dict(self)
        dic["userKey"] = self.user_id
        dic['lopuKey'] = {'e':self.rsa_key['e'], 'n':self.rsa_key['n']}
        dic.pop("user_id")
        dic.pop("rsa_key")
        return dic
    
    def __get_client_language(self):
        language = web.ctx.env.get("HTTP_ACCEPT_LANGUAGE")
        if language is None or language.strip() == '':
            language = "zh_CN"
        else:
            language = language.lower().replace("-", "_")
            languages = language.split(";")
            if len(languages) == 0:
                languages[0] = language
            supported_languages = conf.get_supported_languages()
            if languages[0] in supported_languages:
                language = supported_languages[1]
            else:
                language = supported_languages[0]
        return language
    
def has_token():
        if _get_session().has_key(TOKEN_NAME) and _get_session()[TOKEN_NAME] != None:
            return True
        return False
    
def get_token():
    return _get_session()[TOKEN_NAME]

def set_token(token):
    _get_session()[TOKEN_NAME] = token
    conf.session_hook(token)
    return token

def drop_token():
    _get_session()[TOKEN_NAME] = None

def _get_session():          
    return web.config._session