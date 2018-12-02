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


class IncrExtract(Model):
    
    DEFAULT_START_DELTA = 10.0  # seconds
    DEFAULT_END_DELTA = 0.0  # seconds
    
    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN
    
    ie_name = properti.StringProperty(required=True, validator=[UniqueValidator('ie_name')])    
    code_path = properti.StringProperty(required=True)
    last_time = properti.DateTimeProperty(required=True)  # the last extract time
    first_time = properti.DateTimeProperty(required=False)  # the first extract time
    start_delta = properti.FloatProperty(required=True, default=DEFAULT_START_DELTA)  # the start time delta
    end_delta = properti.FloatProperty(required=True, default=DEFAULT_START_DELTA)  # the end time delta
    
class IncrExtractLog(Model):
    
    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN
    
    ie_id = properti.StringProperty(required=True)
    ie_name = properti.StringProperty(required=True)
    extr_time = properti.DateTimeProperty(required=True, auto_utcnow=True)
