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
import types


CODE_UNKNOWN = 9999


"""
Error Code Range:
error: 1001 ~ 1039
orm: 1040 ~ 1049
web: 1050 ~ 1069
vfs: 1070 ~ 1079
auth: 1100 ~ 1129
asyn:1130 ~ 1139
schedule:1140 ~ 1149
cache: 1150 ~ 1160

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

class NoSupportError(Error):
    def __init__(self, it, something):
        super(NoSupportError, self).__init__("{{it}} {{something}} is not supported.", it=str(it), something=str(something))

    @property
    def code(self):
        return 1005       

class InvalidError(Error):
    def __init__(self, something, why):
        super(InvalidError, self).__init__("{{something}} is not valid because {{why}}.", something=str(something), why=str(why))
    
    @property
    def code(self):
        return 1006

class ClassCastError(Error):
    def __init__(self, clazz, baseclazz):
        super(ClassCastError, self).__init__("{{clazz}} is not the sub-class of {{baseClazz}}." , clazz=clazz, baseClazz=baseclazz)
        
    @property
    def code(self):
        return 1007

class RequiredError(Error):
    def __init__(self, label):
        super(RequiredError, self).__init__("{{label}} is required.", label=label)
    @property
    def code(self):
        return 1010    

class ChoiceError(Error):
    def __init__(self, label, choices):
        super(ChoiceError, self).__init__("The value of {{label}} must be one of {{choices}}.", label=label, choices=",".join(map(str, choices)))
    @property
    def code(self):
        return 1011

class LengthError(Error):
    def __init__(self, label, minlength, maxlength):
        super(LengthError, self).__init__("The length of {{label}} must between {{minlength}} and {{maxlength}}.", label=label, minlength=minlength, maxlength=maxlength)

    @property
    def code(self):
        return 1012         

class RangeError(Error):
    def __init__(self, label, mininum, maximum):
        super(RangeError, self).__init__("The value of {{label}} must between {{mininum}} and {{maximum}}.", label=label, mininum=mininum, maximum=maximum)
    @property
    def code(self):
        return 1013    

class CompareError(Error):
    def __init__(self, label, operator, limitlabel, limit):
        super(CompareError, self).__init__("The value of {{label}} must {{operator}} {{limitlabel}} {{limit}}.", label=label, operator=operator, limit=limit, limitlabel=limitlabel)
    @property
    def code(self):
        return 1014    
                
class TypeIntError(Error):
    def __init__(self, label):
        super(TypeIntError, self).__init__("The value of {{label}} must be an integer.", label=label)
    @property
    def code(self):
        return 1015    
        
class TypeFloatError(Error):
    def __init__(self, label):
        super(TypeFloatError, self).__init__("The value of {{label}} must be a float.", label=label)
    @property
    def code(self):
        return 1016    
        
class TypeDateError(Error):
    def __init__(self, label, fmt=format):
        super(TypeDateError, self).__init__("The value of {{label}} must be the format {{fmt}}.", label=label, fmt=format)
    @property
    def code(self):
        return 1017   

class TypeDatetimeError(Error):
    def __init__(self, label, fmt=format):
        super(TypeDatetimeError, self).__init__("The value of {{label}} must be the format {{fmt}}.", label=label, fmt=format)
    @property
    def code(self):
        return 1018
        
class TypeFormatError(Error):
    def __init__(self, label, fmt=format):
        super(TypeFormatError, self).__init__("The format of {{label}} must be the format {{fmt}}.", label=label, fmt=format)
    @property
    def code(self):
        return 1019

class TypeBoolError(Error):
    def __init__(self, label):
        super(TypeBoolError, self).__init__("The value of {{label}} must be a bool.", label=label)
    @property
    def code(self):
        return 1020   
        
class TypeListError(Error):
    def __init__(self, label):
        super(TypeListError, self).__init__("The value of {{label}} must be instance of list.", label=label)
    @property
    def code(self):
        return 1021   

class TypeDictError(Error):
    def __init__(self, label):
        super(TypeDictError, self).__init__("The value of {{label}} must be instance of dict.", label=label)
    @property
    def code(self):
        return 1022

class TypeFunctionError(Error):
    def __init__(self, label):
        super(TypeFunctionError, self).__init__("The value of {{label}} must be a function.", label=label)
    
    @property
    def code(self):
        return 1023
    
class TypeGeneratorError(Error):
    def __init__(self, label):
        super(TypeGeneratorError, self).__init__("The value of {{label}} must be instance of generator.", label=label)
    
    @property
    def code(self):
        return 1024

class TypeStrError(Error):
    def __init__(self, label):
        super(TypeStrError, self).__init__("The value of {{label}} must be a str.", label=label)
    @property
    def code(self):
        return 1025
    
def assert_required(value, label):
    """
        check if value is None or empty str. 
    """
    if value is None:
        raise RequiredError(label)
    if type(value) == str and len(value.strip()) == 0:        
        raise RequiredError(label)

def assert_type_int(value, label):
    if type(value) != int:
        raise TypeIntError(label)
    return True

def assert_type_float(value, label):
    if type(value) != float:
        raise TypeFloatError(label)
    return True

def assert_type_bool(value, label):
    if type(value) != bool:
        raise TypeBoolError(label)

def assert_type_list(value, label):
    if type(value) != list:
        raise TypeListError(label)

def assert_type_dict(value, label):
    if type(value) != dict:
        raise TypeDictError(label)
    
def assert_type_generator(value, label):
    if type(value) != types.GeneratorType:
        raise TypeGeneratorError(label)

def assert_type_function(value, label):
    if type(value) != types.FunctionType:
        raise TypeFunctionError(label)

def assert_type_str(value, label):
    if type(value) != str:
        raise TypeStrError(label)
    return True

def assert_in(value, choices, label):    
    if value not in choices:
        raise ChoiceError(label, choices)
    return True

def assert_equal(value1, value2, label1, label2):
    if value1 != value2:
        raise CompareError(label1, "=", label2, '')

def assert_not_equal(value1, value2, label1, label2):
    if value1 == value2:
        raise CompareError(label1, "!=", label2, '')

def format_exc_info(exc_info):
    error_class = exc_info[1]
    tb_message = format_traceback(exc_info[2])
    return "%s\n%s" % (str(error_class), tb_message)

def format_traceback(traceback1):
    return "".join(traceback.format_tb(traceback1))
