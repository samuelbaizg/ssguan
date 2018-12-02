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

from ssguan.ignitor.orm import properti
from ssguan.ignitor.orm.model import BaseModel 
from ssguan.ignitor import IGNITOR_DOMAIN

class MCLog(BaseModel):
    
    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN
    
    modelname = properti.StringProperty(required=True, length=80)
    modelkey = properti.StringProperty(required=True)
    user_id = properti.StringProperty(required=True)
    change_props = properti.ListProperty(required=True, length=4294967295)
    change_time = properti.DateTimeProperty(required=True, auto_utcnow=True)
