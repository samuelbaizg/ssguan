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

from functools import wraps

from ssguan.ignitor.utility import kind, crypt
from ssguan.ignitor.web.handler import Rtn


def req_rtn(content_type="application/json"):
    def decorate(func):
        @wraps(func)
        def wrapper(reqHandler, *args, **kwargs):
            reqHandler.set_header("Content-Type", content_type)
            data = func(reqHandler, *args, **kwargs)
            rtn = Rtn(data=data)
            jsonstr = kind.obj_to_json(rtn.to_dict())
            jsonstr = crypt.str_to_base64(jsonstr)
            reqHandler.write(jsonstr)
            reqHandler.finish()
        return wrapper
    return decorate
    