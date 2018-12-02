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

class LoginFailedError(Error):
    def __init__(self):
        super(LoginFailedError, self).__init__(
            "Your email or account is not matched your password, please enter again")

    @property
    def code(self):
        return 1100


class UnauthorizedError(Error):
    def __init__(self, operation_code):
        super(UnauthorizedError, self).__init__(
            "You don't have the permission -- {{operation_code}}.", operation_code=operation_code)

    @property
    def code(self):
        return 1101


class OldPasswordError(Error):
    def __init__(self):
        super(OldPasswordError, self).__init__(
            "You old password is not correct.")

    @property
    def code(self):
        return 1102

class CredentialExpiredError(Error):
    def __init__(self):
        super(CredentialExpiredError, self).__init__(
            "Your credential expired, please login again.")

    @property
    def code(self):
        return 1103