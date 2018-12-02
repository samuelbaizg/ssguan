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
class Error(Exception):
    def __init__(self, code, message="", data=None, *args, **kwargs):
        self.__code = code
        self.__message = message
        self.__data = data
        self.__args = args
        self.__kwargs = kwargs
    
    def get_code(self):
        return self.__code
    
    def get_data(self):
        return self.__data
    
    def get_arguments(self):
        return self.__kwargs
    
    def __str__(self):
        message = self.__message
        if message != None and (self.__args != None and len(self.__args) > 0):
            message = message % self.__args
        return message

# CoreError is to define system error
class CoreError(Error):
    def __init__(self, message, *args):
        super(CoreError, self).__init__("core_error_core", message, None, *args)

class IllegalWordError(Error):
    def __init__(self, label, illegalword):
        super(IllegalWordError, self).__init__("core_error_illegalword", label=label, illegalword=illegalword)

class UniqueError(Error):
    def __init__(self, label, value):
        super(UniqueError, self).__init__("core_error_unique", label=label, value=value)

class RequiredError(Error):
    def __init__(self, label):
        super(RequiredError, self).__init__("core_error_required", label=label)

class ChoiceError(Error):
    def __init__(self, label, choices):
        super(ChoiceError, self).__init__("core_error_choices", label=label, choices=",".join(choices))

class LengthError(Error):
    def __init__(self, label, minlength, maxlength):
        super(LengthError, self).__init__("core_error_length", label=label, minlength=minlength, maxlength=maxlength)     

class RangeError(Error):
    def __init__(self, label, mininum, maximum):
        super(RangeError, self).__init__("core_error_range", label=label, mininum=mininum, maximum=maximum)

class CompareError(Error):
    def __init__(self, label, operator, limit, limitlabel):
        super(CompareError, self).__init__("core_error_compare", label=label, operator=operator, limit=limit, limitlabel=limitlabel)
                
class TypeIntError(Error):
    def __init__(self, label):
        super(TypeIntError, self).__init__("core_error_typeint", label=label)
        
class TypeFloatError(Error):
    def __init__(self, label):
        super(TypeFloatError, self).__init__("core_error_typefloat", label=label)
        
class TypeDateError(Error):
    def __init__(self, label, fmt=format):
        super(TypeDateError, self).__init__("core_error_typedate", label=label, fmt=format)

class TypeDatetimeError(Error):
    def __init__(self, label, fmt=format):
        super(TypeDatetimeError, self).__init__("core_error_typedate", label=label, fmt=format)
        
class TypeFormatError(Error):
    def __init__(self, label, fmt=format):
        super(TypeFormatError, self).__init__("core_error_typewrong", label=label, fmt=format)

class SessionExpiredError(Error):
    def __init__(self, token):
        super(SessionExpiredError, self).__init__("core_error_session_expired", data=token)
        
class LoginFailedError(Error):
    def __init__(self):
        super(LoginFailedError, self).__init__("core_error_login_failed")
        
class UnauthorizedError(Error):
    def __init__(self):
        super(UnauthorizedError, self).__init__("core_error_unauthorized")

class FileSizeExceededError(Error):
    def __init__(self, filesize):
        super(FileSizeExceededError, self).__init__("core_error_filesize_exceeded", filesize=filesize)

class DataExpiredError(Error):
    def __init__(self):
        super(DataExpiredError, self).__init__("core_error_updateexpireddata")  
