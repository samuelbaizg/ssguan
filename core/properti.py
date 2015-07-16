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
import datetime
import os

from core import strutil
from core.error import CoreError, IllegalWordError, UniqueError, \
    RequiredError, ChoiceError, LengthError, RangeError, TypeIntError, \
    TypeFloatError, TypeDateError, TypeDatetimeError, CompareError


class Property(object):

    def __init__(self, name=None, label=None, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        self.name = name
        self._label = label
        self.persistent = persistent
        self.default = default
        self.required = required
        if validator is not None:
            if isinstance(validator, Validator):
                self.validators = []
                self.validators.append(validator)
            elif isinstance(validator, type([])):
                self.validators = validator
            else:
                raise CoreError("validator must be the instance of either Validator or List")
        else:
            self.validators = None
        self.choices = choices
        self.logged = logged
        
    def __property_config__(self, model_class, property_name):
        self.model_class = model_class
        if self.name is None:
            self.name = property_name

    def __get__(self, model_instance, model_class):
        if model_instance is None:
            return self
        try:
            value = getattr(model_instance, self._attr_name())
            return value
        except AttributeError:
            return None

    def __set__(self, model_instance, value):
        if model_instance._is_entityinst():
            value = self.normalize_value(value)
            
        setattr(model_instance, self._attr_name(), value)
        
    def default_value(self):
        return self.default
    
    def get_label(self):
        return self._label
    
    def get_label_i18n_key(self):
        label = self.get_label().lower()
        return ("%s_label_%s" % (self.model_class.MODULE, label)).lower()
    
    def validate(self, value, model_instance):
        if self.empty(value):
            if self.required:
                label = self.get_label_i18n_key()
                raise RequiredError(label)
        else:
            if self.choices:
                if value not in self.choices:
                    label = self.get_label_i18n_key()
                    raise ChoiceError(label, self.choices)
        
        if self.validators is not None:
            label = self.get_label_i18n_key()
            for validator in self.validators:
                value = validator.validate(value, label, model_instance=model_instance)
        return value

    def empty(self, value):
        return value == None

    def _attr_name(self):
        return '_' + self.name
    
    data_type = (basestring)
    
    def db_data_type(self):
        return "varchar(80)"
    
    def normalize_value(self, value):
        return value
    
    def to_string(self, value):
        return value if value is None else str(value)
    
class StringProperty(Property):
    def __init__(self, label, length=80, persistent=True, default=None, required=False, validator=None, fmt=None, choices=None, logged=False):
        super(StringProperty, self).__init__(label=label, name=None, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)
        self.length = length
        self.fmt = fmt

    def validate(self, value, model_instance):
        value = super(StringProperty, self).validate(value, model_instance)
        if value is not None and not isinstance(value, basestring):
            value = str(value)
        if value is not None and len(value) > self.length:
            raise CoreError(
              'Property %s is %d characters long; it must be %d or less.'
              % (self.name, len(value), self.length))
        return value
    
    data_type = (basestring)
    
    def db_data_type(self):
        if self.length <= 10:
            return "char(%d)" % self.length
        if self.length <= 8192:
            return "varchar(%d)" % self.length
        elif self.length <= 65535:
            return "text"
        elif self.length <= 16777215:
            return "mediumtext"
        elif self.length <= 4294967295:
            return "longtext"
        else:
            return "varchar(%d)" % self.length
        
    def normalize_value(self, value):
        return str(value) if value is not None else value
    
    def empty(self, value):
        return strutil.is_empty(value)

class IntegerProperty(Property):
    
    def __init__(self, label, persistent=True, length=11, default=None, required=False, validator=None, choices=None, logged=False):
        super(IntegerProperty, self).__init__(label=label, name=None, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)
        self.length = length
    
    def validate(self, value, model_instance):
        value = super(IntegerProperty, self).validate(value, model_instance)
        if value is None:
            return value
        
        if isinstance(value, str) or isinstance(value, unicode):
            if not strutil.is_int(value):
                raise TypeIntError(self.get_label_i18n_key())
            else:
                value = int(value)
        
        if not isinstance(value, (int, long)) or isinstance(value, bool):
            raise CoreError('Property %s must be an int or long, not a %s'
                              % (self.name, type(value).__name__))
        if value < -0x8000000000000000 or value > 0x7fffffffffffffff:
            raise CoreError('Property %s must fit in 64 bits' % self.name)
        return value

    def empty(self, value):    
        return value is None
    
    data_type = (int, long)
    def db_data_type(self):
        return "int(%d)" % self.length 
    
    def normalize_value(self, value):
        return value if type(value) is int else strutil.to_int(value)

class FloatProperty(Property):
    
    def __init__(self, label, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(FloatProperty, self).__init__(label=label, name=None, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        value = super(FloatProperty, self).validate(value, model_instance)
        
        if isinstance(value, str) or isinstance(value, unicode):
            if not strutil.is_float(value):
                raise TypeFloatError(self.get_label_i18n_key())
            else:
                value = float(value)
        
        if value is not None and not isinstance(value, float):
            raise CoreError('Property %s must be a float' % self.name)
        return value

    def empty(self, value):
        return value is None
    
    data_type = (float)
    def db_data_type(self):
        return "float"
    
    def normalize_value(self, value):
        return value if type(value) is float else strutil.to_float(value)

class BooleanProperty(Property):
    
    def __init__(self, label, persistent=True, required=True, default=False, validator=None, logged=False):
        super(BooleanProperty, self).__init__(label=label, name=None, persistent=persistent, default=default, required=required, validator=validator, logged=logged)

    def validate(self, value, model_instance):
        value = super(BooleanProperty, self).validate(value, model_instance)
        if value is not None and not isinstance(value, bool):
            raise CoreError('Property %s must be a bool' % self.name)
        return value

    def empty(self, value):
        return value is None
    
    data_type = (bool, int)    
    def db_data_type(self):
        return "tinyint(1)"
    
    def normalize_value(self, value):
        if isinstance(value, int):
            if value >= 1:
                value = True
            else:
                value = False
        return value

class DateTimeProperty(Property):

    def __init__(self, label, persistent=True, auto_utcnow=False, required=False, validator=None, fmt=None, logged=False):
        super(DateTimeProperty, self).__init__(label=label, name=None, persistent=persistent, default=None, required=required, validator=validator, logged=logged)
        self.auto_now = auto_utcnow
        self.fmt = fmt

    def validate(self, value, model_instance):
        value = super(DateTimeProperty, self).validate(value, model_instance)
        
        if isinstance(value, str) or isinstance(value, unicode):
            if not strutil.is_datetime(value, fmt=self.fmt):
                raise TypeDatetimeError(self.get_label_i18n_key())
            else:
                value = strutil.to_datetime(value, fmt=self.fmt)
        
        if value and not isinstance(value, self.data_type):
            raise CoreError('Property %s must be a %s' % 
                              (self.name, self.data_type.__name__))
        return value

    def default_value(self):
        if self.auto_now:
            now = self.utcnow()
            return now
        else:
            return Property.default_value(self)

    @staticmethod
    def utcnow():
        return datetime.datetime.utcnow()
    
    data_type = (datetime.datetime)
    def db_data_type(self):
        return "datetime"
    
    def normalize_value(self, value):
        if isinstance(value, datetime.datetime):
            return value
        else:
            return strutil.to_datetime(value, fmt=self.fmt)
        
    def to_string(self, value):
        return value if value is None else self.normalize_value(value).strftime(self.fmt)

class DateProperty(Property):
    
    def __init__(self, label, persistent=True, auto_utctoday=False, required=False, validator=None, fmt=None, logged=False):
        super(DateProperty, self).__init__(label=label, name=None, persistent=persistent, default=None, required=required, validator=validator, logged=logged)
        self.auto_today = auto_utctoday
        self.fmt = fmt

    def validate(self, value, model_instance):
        value = super(DateProperty, self).validate(value, model_instance)
        
        if isinstance(value, str) or isinstance(value, unicode):
            if not strutil.is_date(value, fmt=self.fmt):
                raise TypeDateError(self.get_label_i18n_key())
            else:
                value = strutil.to_date(value, fmt=self.fmt)
        
        if value and not isinstance(value, self.data_type):
            raise CoreError('Property %s must be a %s',
                              self.name, self.data_type.__name__)
        return value

    def default_value(self):
        if self.auto_today:
            today = self.utctoday()
            return today
        else:
            return Property.default_value(self)
    
    @staticmethod
    def utctoday():
        now = datetime.datetime.utcnow()
        return datetime.date(now.year, now.month, now.day)
    
    data_type = datetime.date
    def db_data_type(self):
        return "date"
    
    def normalize_value(self, value):
        if isinstance(value, datetime.date):
            return value
        else:
            return strutil.to_date(value, fmt=self.fmt)
        
    def to_string(self, value):
        return value if value is None else self.normalize_value(value).strftime(self.fmt)

class BlobProperty(Property):
    def __init__(self, label, persistent=True, required=False, validator=None):
        super(BlobProperty, self).__init__(label=label, name=None, persistent=persistent, default=None, required=required, validator=validator)

    def validate(self, value, model_instance):
        value = super(BlobProperty, self).validate(value, model_instance)
        return value

    data_type = datetime.date
    def db_data_type(self):
        return "longblob"
    

class Validator(object):
    
    def validate(self, value, label, model_instance=None):
        """To be override by sub-class"""
        raise NotImplementedError

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
            raise CoreError("the illegal words are not loaded.")
        if value != None and isinstance(value, basestring) and len(value) > 0:
            for ilword in ilwords:
                if (ilword in value):
                    if self.__replace:
                        value = value.replace(ilword, self.__chars)
                    else:
                        raise IllegalWordError(label, ilword)
        return value
    
    def __load_illegalwords(self):
        ilwords = []
        iwpath = os.path.dirname(__file__) + os.sep + "illegalwords.txt"
        if os.path.exists(iwpath):
#            iwfile = file(iwpath, 'r')
            iwfile = codecs.open(iwpath, encoding='utf-8')
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
            raise CoreError("%s is not found." , iwpath)
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
                raise CoreError("The type of scope only can be String or List.")
        
    def validate(self, value, label, model_instance):
        if self._scope is not None:
            for scope in self._scope:
                    if not model_instance.is_persistent(scope):
                        raise CoreError("The scope %s is not a persistent property in model %s." % (scope, model_instance.__class__))
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
    def __init__(self, minimum, maximum):
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
            raise CoreError("RangeValidator doesn't support type %s" , type(value))
        return value

class CompareValidator(Validator):
    
    _OPERATORS = ('=', '>=', '<=', ">", "<") 
    
    def __init__(self, operator, limit=None, property_name=None):
        super(CompareValidator, self).__init__()
        if operator is None or operator not in self._OPERATORS:
            raise CoreError("operator %s is not in %r" , operator, self._OPERATORS)
        if limit is None and property_name is None:
            raise CoreError("One of limit and property_name must be assigned.")
        if limit is not None and property_name is not None:
            raise CoreError("Only one of limit and property_name can be assigned.")
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
            limlabel = prop.get_label_i18n_key()
        if self._operator == '=' and lim is not None and value != lim:
            raise CompareError(label, self._operator, lim, limlabel)
        elif self._operator == '>=' and lim is not None and value < lim:
            raise CompareError(label, self._operator, lim, limlabel)
        elif self._operator == '<=' and lim is not None and value > lim:
            raise CompareError(label, self._operator, lim, limlabel)
        elif self._operator == '>' and lim is not None and value <= lim:
            raise CompareError(label, self._operator, lim, limlabel)
        elif self._operator == '<' and lim is not None and value >= lim:
            raise CompareError(label, self._operator, lim, limlabel)
        return value
        
        
        
        
        
        
        
