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
import traceback


CODE_UNKNOWN = 9999

"""
Error Code Range:
error: 1001 ~ 1005
update: 1006 ~ 1009
model: 1010 ~ 1019
property: 1020 ~ 1049
web: 1050 ~ 1069
filesys: 1070 ~ 1079
auth: 1100 ~ 1129
mqueue:1130 ~ 1139
schedule:1140 ~ 1149

"""
class ExceptionWrap(Exception):
    
    def __init__(self, exc_info, **data):
        if isinstance(exc_info, Exception):
            exc_info = (exc_info.__class__, exc_info, None)
        if exc_info is None:
            raise Exception("exc_info can't be null.")
        if not isinstance(exc_info, tuple) or len(exc_info) != 3:
            raise Exception("exc_info must be a type of exc_info.")
        self.__exc_info = exc_info
        self.__data = data
        
    @property
    def exception(self):
        return self.__exc_info[1]
    
    @property
    def traceback(self):
        return self.__exc_info[2]
    
    @property
    def data(self):
        return self.__data
    
    @property
    def message(self):
        return str(self.exception)
    
    @property
    def message_tb(self):
        return  "".join(traceback.format_tb(self.traceback))
    
    def __str__(self):
        return self.message

class Error(Exception):
    def __init__(self, message, *args, **kwargs):
        self.__message = message
        self.__args = args
        self.__kwargs = kwargs
    
    @property
    def code(self):
        """To be implemented by sub-class"""
        raise NotImplementedError("Error.code")
    
    @property
    def message(self):
        message = self.__message
        if message != None and (self.__args != None and len(self.__args) > 0):
            message = message % self.__args
        if message != None and (self.__kwargs != None and len(self.__kwargs) > 0):
            for key, value in self.__kwargs.items():
                message = message.replace("{{%s}}" % key, str(value))
        return "%d: %s" % (self.code, message)
    
    @property
    def arguments(self):
        return self.__kwargs
    
    def get_argument(self, key):
        return self.arguments[key]
    
    def __str__(self):
        return self.message

class ProgramError(Error):
    """
        ProgramError is to define the error for programmer codes.
    """
    def __init__(self, message, *args):
        super(ProgramError, self).__init__(message, *args)
    
    @property
    def code(self):
        return 1001
    
class RunError(Error):
    """
        RunError is to define the error for runtime.
    """
    def __init__(self, message, *args):
        super(RunError, self).__init__(message, *args)
    
    @property
    def code(self):
        return 1002

class NoDoError(Error): 
    def __init__(self, action, what):
        super(NoDoError, self).__init__("No support to {{action}} {{what}}", action=action, what=what)
    
    @property
    def code(self):
        return 1003
    
class NoFoundError(Error):
    def __init__(self, it, something):
        super(NoFoundError, self).__init__("{{it}} {{something}} is not found.", it=str(it), something=str(something))
    
    @property
    def code(self):
        return 1004              

class InvalidParamError(Error):
    def __init__(self, name):
        super(InvalidParamError, self).__init__("parameter {{name}} is invalid.", name=name)
    
    @property
    def code(self):
        return 1005     