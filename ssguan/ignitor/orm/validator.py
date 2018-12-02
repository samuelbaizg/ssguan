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

import codecs
import os
import datetime
from ssguan.ignitor.base.error import ProgramError, LengthError, RangeError, CompareError
from ssguan.ignitor.orm.error import IllegalWordError, UniqueError


class Validator(object):
    
    def validate(self, value, label, model_instance=None):
        """To be override by sub-class"""
        raise NotImplementedError("Validator.validate")

illegalwords = []

class IllegalValidator(Validator):
    
    def __init__(self, replace=False, chars="***"):
        super(IllegalValidator, self).__init__()
        self.__replace = replace
        self.__chars = chars
        global illegalwords
        if illegalwords == None or len(illegalwords) == 0:
            illegalwords = self.__load_illegalwords()
            
    def validate(self, value, label, model_instance=None):
        global illegalwords
        ilwords = illegalwords
        if ilwords == None or len(ilwords) == 0:
            raise ProgramError("the illegal words are not loaded.")
        if value != None and isinstance(value, str) and len(value) > 0:
            for ilword in ilwords:
                if (ilword in value):
                    if self.__replace:
                        value = value.replace(ilword, self.__chars)
                    else:
                        raise IllegalWordError(label, ilword)
        return value
    
    def __load_illegalwords(self):
        ilwords = []
        iwpath = os.path.join(os.path.dirname(__file__) , "illegalwords.txt")
        if os.path.exists(iwpath):
            with codecs.open(iwpath, encoding='utf-8') as iwfile:
                iwords = iwfile.readlines()
                for iword in iwords:
                    if len(iword) >= 1:
                        if iword.endswith('\n'):
                            iword = iword[0:-1]
                        if iword.endswith('\r'):
                            iword = iword[0:-1]
                        if iword.endswith(';'):
                            iword = iword[0:-1]
                        if len(iword) > 0:
                            ilwords.append(iword)
        else:
            raise ProgramError("%s is not found." , iwpath)
        return ilwords

class UniqueValidator(Validator):
    
    def __init__(self, property_name, scope=None):
        super(UniqueValidator, self).__init__()
        self._scope = scope
        self._property_name = property_name
        if scope != None:
            if type(scope) == str:
                self._scope = []
                self._scope.append(scope)
            elif type(scope) == type([]):
                self._scope = scope
            else:
                raise ProgramError("The type of scope only can be String or List.")
        
    def validate(self, value, label, model_instance):
        if self._scope is not None:
            for scope in self._scope:
                    if not model_instance.is_persistent(scope):
                        raise ProgramError("The scope %s is not a persistent property in model %s." % (scope, model_instance.__class__))
        prop = model_instance.get_properties()[self._property_name]
        query = model_instance.all()
        query = query.filter("%s =" % prop.name, value)
        if model_instance.get_keyvalue() != None:
            query.filter("%s !=" % model_instance.get_keyname(), model_instance.get_keyvalue())
        
        if self._scope is not None:
            for scope in self._scope:
                scopevalue = getattr(model_instance, scope)
                query.filter("%s =" % scope, scopevalue)
        if query.count() > 0:
            raise UniqueError(label, value)
        return value
        
class LengthValidator(Validator):
    
    def __init__(self, minlength=0, maxlength=100000):
        super(LengthValidator, self).__init__()
        self._minlength = minlength
        self._maxlength = maxlength
        
    def validate(self, value, label, model_instance=None):
        if value is None:
            return value
        value = str(value)
        
        length = len(value)
        if length > self._maxlength or length < self._minlength:
            raise LengthError(label, self._minlength, self._maxlength)
        return value

class RangeValidator(Validator):
    def __init__(self, minimum, maximum=0x7fffffffffffffff):
        super(RangeValidator, self).__init__()
        self._minimum = minimum
        self._maximum = maximum
        
    def validate(self, value, label, model_instance=None):
        if value is None:
            return value
        
        if type(value) is str or type(value) is int or type(value) is float:
            if value < self._minimum or value > self._maximum:
                raise RangeError(label, self._minimum, self._maximum)
        elif type(value) is datetime.datetime or type(value) is datetime.date:
            if value < self._minimum or value > self._maximum:
                raise RangeError(label, self._minimum, self._maximum)
        else:
            raise ProgramError("RangeValidator doesn't support type %s" , type(value))
        return value

class CompareValidator(Validator):
    
    _OPERATORS = ('=', '>=', '<=', ">", "<") 
    
    def __init__(self, operator, limit=None, property_name=None):
        super(CompareValidator, self).__init__()
        if operator is None or operator not in self._OPERATORS:
            raise ProgramError("operator %s is not in %r" , operator, self._OPERATORS)
        if limit is None and property_name is None:
            raise ProgramError("One of limit and property_name must be assigned.")
        if limit is not None and property_name is not None:
            raise ProgramError("Only one of limit and property_name can be assigned.")
        self._operator = operator
        self._limit = limit
        self._property_name = property_name
    
    def validate(self, value, label, model_instance=None):
        if value is None:
            return value
        
        lim = self._limit
        limlabel = None
        if lim is None:            
            lim = getattr(model_instance, self._property_name)
            prop = model_instance.get_property(self._property_name)
            limlabel = prop.get_label()
        if self._operator == '=' and lim is not None and value != lim:
            raise CompareError(label, self._operator, limlabel, lim)
        elif self._operator == '>=' and lim is not None and value < lim:
            raise CompareError(label, self._operator, limlabel, lim)
        elif self._operator == '<=' and lim is not None and value > lim:
            raise CompareError(label, self._operator, limlabel, lim)
        elif self._operator == '>' and lim is not None and value <= lim:
            raise CompareError(label, self._operator, limlabel, lim)
        elif self._operator == '<' and lim is not None and value >= lim:
            raise CompareError(label, self._operator, limlabel, lim)
        return value
        