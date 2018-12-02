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

from ssguan.ignitor import IGNITOR_DOMAIN
from ssguan.ignitor.orm import properti
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.orm.validator import UniqueValidator


class Registry(Model):
    
    ROOT_KEY = 'ROOT'
    
    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN
    
    item_key = properti.StringProperty(required=True, validator=[UniqueValidator('item_key')])    
    parent_key = properti.StringProperty(required=True, default=ROOT_KEY)
    item_value = properti.ObjectProperty(required=True, length=255)
    item_desc = properti.StringProperty(required=False, length=255)
    valid_flag = properti.BooleanProperty(required=True, default=False)
    
