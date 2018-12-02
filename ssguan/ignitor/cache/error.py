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

from ssguan.ignitor.base.error import Error

class KeyLengthError(Error):
    def __init__(self, key, max_length):
        super(KeyLengthError, self).__init__("Cache key {{key}} is over the {{max_length}}.", key=key, max_length=max_length)
    @property
    def code(self):
        return 1150   
    
class KeyCharError(Error):
    def __init__(self, key, chars):
        super(KeyCharError, self).__init__("Cache key {{key}} contains invisible characters {{chars}}.", key=key, chars=chars)
    @property
    def code(self):
        return 1151   