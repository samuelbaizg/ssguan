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


class SessionInvalidError(Error):
    def __init__(self):
        super(SessionInvalidError, self).__init__(
            "Session is invalid, please login again.")

    @property
    def code(self):
        return 1051

class WrongParamError(Error):
    def __init__(self, uri, method):
        super(WrongParamError, self).__init__(
            "The parameters from uri {{uri}} with method {{method}} is not correct.", uri=uri, method=method)

    @property
    def code(self):
        return 1054