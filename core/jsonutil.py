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
import datetime
import json

from core.model import BaseModel


class ExtJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            df = '%Y-%m-%d %H:%M:%S'
            encoded_object = obj.strftime(df)
        elif isinstance(obj, datetime.date):
            df = '%Y-%m-%d'
            encoded_object = obj.strftime(df)
        elif isinstance(obj, BaseModel):
            encoded_object = obj.to_dict()
        else:
            encoded_object = json.JSONEncoder.default(self, obj)
        return encoded_object

def to_json(dic, wrapper=True):
    if wrapper:
            return json.dumps(dic, ensure_ascii=False, cls=ExtJsonEncoder)
    else:
        return json.dumps(dic['value'], ensure_ascii=False, cls=ExtJsonEncoder)

def to_dict(jsonstr):
    if jsonstr is not None and jsonstr.strip() != '':
        return json.loads(jsonstr)
    else:
        return None