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
from decimal import Decimal
import os
import re

from ssguan.commons import database, typeutils
from ssguan.commons.error import  ProgramError, Error


class Property(object):

    def __init__(self, name=None, label=None, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        self._name = name
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
                raise ProgramError("validator must be the instance of either Validator or List")
        else:
            self.validators = None
        self.choices = choices
        self.logged = logged
        
    def __property_config__(self, model_class, property_name):
        self.model_class = model_class
        if self._name is None:
            self._name = property_name

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
        
    
    @property
    def name(self):
        return self._name
    
    def default_value(self):
        return self.default
    
    def get_label(self):
        return self._label
    
    def validate(self, value, model_instance):
        if self.empty(value):
            if self.required:
                label = self.get_label()
                raise RequiredError(label)
        else:
            if self.choices:
                if value not in self.choices:
                    label = self.get_label()
                    raise ChoiceError(label, self.choices)
        
        if self.validators is not None:
            label = self.get_label()
            for validator in self.validators:
                value = validator.validate(value, label, model_instance=model_instance)
        return value

    def empty(self, value):
        return value == None

    def _attr_name(self):
        return '_p_' + self._name
    
    data_type = (basestring)
    
    def db_data_type(self):
        return "varchar(80)"
    
    def normalize_value(self, value):
        """
            Convert value to the Python type
        """
        return value
    
    def serialize_value(self, value):
        """
            Convert value to the DB type
        """
        return value
    
    def to_string(self, value):
        return value if value is None else str(value)
    
class StringProperty(Property):
    def __init__(self, label, length=80, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(StringProperty, self).__init__(label=label, name=None, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)
        self.length = length

    def validate(self, value, model_instance):
        value = super(StringProperty, self).validate(value, model_instance)
        if value is not None and not isinstance(value, basestring):
            value = str(value)
        if value is not None and len(value) > self.length:
            raise LengthError(self._label, 0, self.length)
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
        return typeutils.str_is_empty(value)

class IntegerProperty(Property):
    
    def __init__(self, label, persistent=True, length=11, default=None, required=False, validator=None, choices=None, logged=False):
        super(IntegerProperty, self).__init__(label=label, name=None, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)
        self.length = length
    
    def validate(self, value, model_instance):
        value = super(IntegerProperty, self).validate(value, model_instance)
        if value is None:
            return value
        
        if isinstance(value, str) or isinstance(value, unicode):
            if not typeutils.str_is_int(value):
                raise TypeIntError(self.get_label())
            else:
                value = int(value)
        
        if not isinstance(value, (int, long)) or isinstance(value, bool):
            raise TypeIntError(self._label)
        if (len(str(value)) > self.length):
            raise LengthError(self._label, 0, self.length)
        if value < -0x8000000000000000 or value > 0x7fffffffffffffff:
            raise ProgramError('Property %s must fit in 64 bits' % self._name)
        return value

    def empty(self, value):    
        return value is None
    
    data_type = (int, long)
    def db_data_type(self):
        return "int(%d)" % self.length 
    
    def normalize_value(self, value):
        return value if type(value) is int else typeutils.str_to_int(value)

class FloatProperty(Property):
    
    def __init__(self, label, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(FloatProperty, self).__init__(label=label, name=None, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        value = super(FloatProperty, self).validate(value, model_instance)
        
        if isinstance(value, str) or isinstance(value, unicode):
            if not typeutils.str_is_float(value):
                raise TypeFloatError(self.get_label())
            else:
                value = float(value)
        
        if value is not None and not isinstance(value, float):
            raise TypeFloatError(self._label)
        return value

    def empty(self, value):
        return value is None
    
    data_type = (float)
    def db_data_type(self):
        return "float"
    
    def normalize_value(self, value):
        return value if type(value) is float else typeutils.str_to_float(value)

class BooleanProperty(Property):
    
    def __init__(self, label, persistent=True, required=True, default=False, validator=None, logged=False):
        super(BooleanProperty, self).__init__(label=label, name=None, persistent=persistent, default=default, required=required, validator=validator, logged=logged)

    def validate(self, value, model_instance):
        value = super(BooleanProperty, self).validate(value, model_instance)
        if value is not None and not isinstance(value, bool):
            raise TypeBoolError(self._label)
        return value

    def empty(self, value):
        return value is None
    
    data_type = (bool, int)    
    def db_data_type(self):
        return "tinyint(1)"
    
    def serialize_value(self, value):
        if value == True:
            value = 1
        else:
            value = 0
        return value
    
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
            if not typeutils.str_is_datetime(value, fmt=self.fmt):
                raise TypeDatetimeError(self.get_label())
            else:
                value = typeutils.str_to_datetime(value, fmt=self.fmt)
                value = typeutils.local_to_utc(value)
        
        if value and not isinstance(value, self.data_type):
            raise TypeDatetimeError(self._label, self.fmt)
        return value

    def default_value(self):
        if self.auto_now:
            now = self.utcnow()
            return now
        else:
            return Property.default_value(self)

    @staticmethod
    def utcnow():
        return typeutils.utcnow()
    
    data_type = (datetime.datetime)
    def db_data_type(self):
        return "datetime"
    
    def serialize_value(self, value):
        if value is not None:
            value = typeutils.local_to_utc(value)
            value = value.replace(tzinfo=None)
        return value
    
    def normalize_value(self, value):
        if not isinstance(value, datetime.datetime):
            value = typeutils.str_to_datetime(value, fmt=self.fmt)
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=typeutils.tz_utc())
        return value
        
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
            if not typeutils.str_is_date(value, fmt=self.fmt):
                raise TypeDateError(self.get_label())
            else:
                value = typeutils.str_to_date(value, fmt=self.fmt)
        if isinstance(value , datetime.datetime):
            value = typeutils.datetime_to_date(value)
        if value and not isinstance(value, self.data_type):
            raise TypeDateError(self._label, self.fmt)
        return value

    def default_value(self):
        if self.auto_today:
            today = self.utctoday()
            return today
        else:
            return Property.default_value(self)
    
    @staticmethod
    def utctoday():
        return typeutils.utctoday()
    
    data_type = datetime.date
    def db_data_type(self):
        return "date"
    
    def serialize_value(self, value):
        if isinstance(value, datetime.datetime):
            return typeutils.datetime_to_date(value)
        return value
    
    def normalize_value(self, value):
        if isinstance(value, datetime.datetime):
            return typeutils.datetime_to_date(value)
        elif isinstance(value, datetime.date):
            return value
        else:
            return typeutils.str_to_date(value, fmt=self.fmt)
        
    def to_string(self, value):
        return value if value is None else self.normalize_value(value).strftime(self.fmt)

class TimezoneProperty(StringProperty):
    
    def __init__(self, label, default=None, logged=False):
        super(TimezoneProperty, self).__init__(label=label, required=True, length=40, default=default, logged=logged)

    def serialize_value(self, value):
        return str(value)
    
    def normalize_value(self, value):
        return typeutils.tz_timezone(value)

class ListProperty(StringProperty):
    def __init__(self, label, length=4096, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(ListProperty, self).__init__(label=label, length=length, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        if value is not None and type(value) != list:
            raise TypeListError(self._label)
        value1 = self.serialize_value(value)
        if value1 is not None and len(value1) > self.length:
            raise LengthError(self._label, 0, self.length)
        return value
    
    def serialize_value(self, value):
        if value is None:
            return value
        else:
            return typeutils.obj_to_json(value)
    
    def normalize_value(self, value):
        value = self.to_string(value)
        if typeutils.str_is_empty(value):
            return None
        else:
            return typeutils.json_to_object(value)


class DictProperty(StringProperty):
    def __init__(self, label, length=4096, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(DictProperty, self).__init__(label=label, length=length, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        if value is not None and type(value) != dict:
            raise TypeDictError(self._label)
        value1 = self.serialize_value(value)
        if value1 is not None and len(value1) > self.length:
            raise LengthError(self._label, 0, self.length)
        return value
    
    def serialize_value(self, value):
        if value is None:
            return value
        else:
            return typeutils.obj_to_json(value)
    
    def normalize_value(self, value):
        value = self.to_string(value)
        if typeutils.str_is_empty(value):
            return None
        else:
            return typeutils.json_to_object(value)

class ObjectProperty(StringProperty):
    def __init__(self, label, length=4096, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(ObjectProperty, self).__init__(label=label, length=length, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        value1 = self.serialize_value(value)
        if value1 is not None and len(value1) > self.length:
            raise LengthError(self._label, 0, self.length)
        return value
    
    def serialize_value(self, value):
        if value is None:
            return None
        else:
            return typeutils.obj_to_pickle(value)
    
    def normalize_value(self, value):
        value = self.to_string(value)
        if typeutils.str_is_empty(value):
            return None
        else:
            return typeutils.pickle_to_obj(value)
        
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
        iwpath = os.path.join(os.path.dirname(__file__) , "illegalwords.txt")
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
        
        

class IllegalWordError(Error):
    def __init__(self, label, illegalword):
        super(IllegalWordError, self).__init__("{{label}} includes the illegal word {{illegalword}}", label=label, illegalword=illegalword)
    @property
    def code(self):
        return 1020    
    
class RequiredError(Error):
    def __init__(self, label):
        super(RequiredError, self).__init__("{{label}} is required.", label=label)
    @property
    def code(self):
        return 1021    

class ChoiceError(Error):
    def __init__(self, label, choices):
        super(ChoiceError, self).__init__("The value of {{label}} must be one of {{choices}}.", label=label, choices=",".join(choices))
    @property
    def code(self):
        return 1022

class LengthError(Error):
    def __init__(self, label, minlength, maxlength):
        super(LengthError, self).__init__("The length of {{label}} must between {{minlength}} and {{maxlength}}.", label=label, minlength=minlength, maxlength=maxlength)

    @property
    def code(self):
        return 1023         

class RangeError(Error):
    def __init__(self, label, mininum, maximum):
        super(RangeError, self).__init__("The value of {{label}} must between {{mininum}} and {{maximum}}.", label=label, mininum=mininum, maximum=maximum)
    @property
    def code(self):
        return 1024    
    

class CompareError(Error):
    def __init__(self, label, operator, limit, limitlabel):
        super(CompareError, self).__init__("The value of {{label}} must {{operator}} {{limitlabel}}{{limit}}.", label=label, operator=operator, limit=limit, limitlabel=limitlabel)
    @property
    def code(self):
        return 1025    
    
                
class TypeIntError(Error):
    def __init__(self, label):
        super(TypeIntError, self).__init__("The value of {{label}} must be an integer.", label=label)
    @property
    def code(self):
        return 1026    
        
class TypeFloatError(Error):
    def __init__(self, label):
        super(TypeFloatError, self).__init__("The value of {{label}} must be a float.", label=label)
    @property
    def code(self):
        return 1027    
        
class TypeDateError(Error):
    def __init__(self, label, fmt=format):
        super(TypeDateError, self).__init__("The value of {{label}} must be the format {{fmt}}.", label=label, fmt=format)
    @property
    def code(self):
        return 1028    

class TypeDatetimeError(Error):
    def __init__(self, label, fmt=format):
        super(TypeDatetimeError, self).__init__("The value of {{label}} must be the format {{fmt}}.", label=label, fmt=format)
    @property
    def code(self):
        return 1029
        
class TypeFormatError(Error):
    def __init__(self, label, fmt=format):
        super(TypeFormatError, self).__init__("The format of {{label}} must be the format {{fmt}}.", label=label, fmt=format)
    @property
    def code(self):
        return 1030    

class LinkedError(Error):
    def __init__(self, mainlabel, linklabel):
        super(LinkedError, self).__init__("{{mainlabel}} is related to {{linklabel}}.", mainlabel=mainlabel, linklabel=linklabel)
    @property
    def code(self):
        return 1031    

class UniqueError(Error):
    def __init__(self, label, value):
        super(UniqueError, self).__init__("The value {{value}} of {{label}} has existed." , label=label, value=value)
    @property
    def code(self):
        return 1032    

class TypeBoolError(Error):
    def __init__(self, label):
        super(TypeBoolError, self).__init__("The value of {{label}} must be a bool.", label=label)
    @property
    def code(self):
        return 1033   
        
class ClassCastError(Error):
    def __init__(self, clazz, baseclazz):
        super(ClassCastError, self).__init__("{{clazz}} is not the sub-class of {{baseClazz}}." , clazz=clazz, baseClazz=baseclazz)
        
    @property
    def code(self):
        return 1135

class TypeListError(Error):
    def __init__(self, label):
        super(TypeListError, self).__init__("The value of {{label}} must be instance of list.", label=label)
    @property
    def code(self):
        return 1036   

class TypeDictError(Error):
    def __init__(self, label):
        super(TypeDictError, self).__init__("The value of {{label}} must be instance of dict.", label=label)
    @property
    def code(self):
        return 1037   

class PropertiedClass(type):
    def __init__(cls, name, bases, dct, map_kind=True):
        super(PropertiedClass, cls).__init__(name, bases, dct)
        _initialize_properties(cls, name, bases, dct)

def _initialize_properties(model_class, name, bases, dct):
    model_class._properties = {}
    property_source = {}
    
    def get_attr_source(name, cls):
        for src_cls  in cls.mro():
            if name in src_cls.__dict__:
                return src_cls

    defined = set()
    for base in bases:
        if hasattr(base, '_properties'):
            property_keys = set(base._properties.keys())
            duplicate_property_keys = defined & property_keys
            for dupe_prop_name in duplicate_property_keys:
                old_source = property_source[dupe_prop_name] = get_attr_source(
                    dupe_prop_name, property_source[dupe_prop_name])
                new_source = get_attr_source(dupe_prop_name, base)
                if old_source != new_source:
                    raise ProgramError(
                      'Duplicate property, %s, is inherited from both %s and %s.',
                      dupe_prop_name, old_source.__name__, new_source.__name__)
    
            property_keys -= duplicate_property_keys
            if property_keys:
                defined |= property_keys
                property_source.update(dict.fromkeys(property_keys, base))
                model_class._properties.update(base._properties)
                
    for attr_name in dct.keys():
        attr = dct[attr_name]
        if isinstance(attr, Property):
            if attr_name in defined:
                raise ProgramError('Duplicate property: %s' % attr_name)
            defined.add(attr_name)
            model_class._properties[attr_name] = attr
            attr.__property_config__(model_class, attr_name)

class BaseModel(typeutils.JsonMixin):
    __metaclass__ = PropertiedClass
    
    DEFAULT_KEYNAME = '_id'
    
       
    _id = StringProperty("key", length=40)
    
    @classmethod
    def meta_domain(cls):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseModel.meta_domain")
    
    def __new__(cls, *args, **unused_kwds):
        bm = super(BaseModel, cls).__new__(cls)
        return bm
    
    
    def __init__(self, entityinst=False, **kwds):
        self._extproperties = {}
        self._entityinst = entityinst
        for prop in self._properties.values():
            value = prop.default_value()
            if value != None:
                prop.__set__(self, value)
        
        if kwds != None:
            for (key, value) in kwds.items():
                setattr(self, key, value)
                    
    def __getattr__(self, name):
        if name != "_extproperties" and "__" not in name:
            tname = name
            
            if tname.find("_p_") == 0:
                tname = name[3:]
            if tname not in self._properties.keys():
                return self._extproperties[name]
            else:
                if hasattr(object, name):
                    return object.__getattr__(self, name)
                else:
                    return None
        else:
            return object.__getattr__(self, name)
    
    def __setattr__(self, name, value):
        if name != "_extproperties" and name != "_entityinst" and name != "_dbconn":
            value = self._normalize_property_value(name, value)
            tname = name
            if not tname.startswith("__") and tname.find("_p_") == 0:
                tname = name[3:]
            if tname not in self._properties.keys():
                self._extproperties[name] = value
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)
            
    def __hasattr__(self, name):
        if self._properties.has_key(name):
            return True
        elif self._extproperties.has_key(name):
            return True
        else:
            return False
        
    @classmethod
    def create_schema(cls, dbconn=None):
        return cls._get_dbconn(dbconn).create_schema(cls)
        
    @classmethod    
    def delete_schema(cls, dbconn=None):
        return cls._get_dbconn(dbconn).delete_schema(cls)
    
    @classmethod
    def has_schema(cls, dbconn=None):
        return cls._get_dbconn(dbconn).has_schema(cls)
    
    @classmethod
    def exist_property(cls, property_name, dbconn=None):
        return cls._get_dbconn(dbconn).exist_property(cls, property_name)
    
    @classmethod
    def add_property(cls, property_name, property_instance, dbconn=None):
        return cls._get_dbconn(dbconn).add_property(cls, property_name, property_instance)
    
    @classmethod
    def change_property(cls, old_property_name, new_property_name, property_instance, dbconn=None):
        return cls._get_dbconn(dbconn).change_property(cls, old_property_name, new_property_name, property_instance)
    
    @classmethod
    def drop_property(cls, property_name, dbconn=None):
        return cls._get_dbconn(dbconn).drop_property(cls, property_name)
    
    @classmethod    
    def get_modelname(cls):
        if cls.meta_domain() is None:
            raise ProgramError("MODULE is not defined in the model %s" , cls.__name__)
        return ("%s_%s" % (cls.meta_domain() , cls.__name__)).lower()

    @classmethod
    def get_keyname(cls):
        return cls.DEFAULT_KEYNAME
    
    @classmethod
    def is_auto_gen_key(cls):
        return True
    
    def get_keyvalue(self):
        return getattr(self, self.get_keyname())
    
    @classmethod
    def get_properties(cls, persistent=None, labelkey=False, excluded=False):
        """
            excluded means the key fields [created_time, created_by, modified_time, modified_by,row_version] are excluded in return dict
        """
        exclusion = ['created_time', 'created_by', 'modified_time', 'modified_by', 'row_version'] if excluded else []            
        props = {}
        for key, prop in cls._properties.items():
            if not key.startswith("_p_") and (persistent is None or prop.persistent == persistent):
                if key not in exclusion:
                    if labelkey:
                        props[prop.get_label()] = prop
                    else:
                        props[key] = prop
        return props
    
    @classmethod
    def get_propnames(cls):
        """
            Return dict with key = label_name and value = prop_name
        """
        m = {}
        for key, prop in cls._properties.items():
            m[prop.get_label()] = key
        return m
    
    @classmethod
    def get_property(cls, propname):
        return cls._properties[propname]
    
    @classmethod
    def is_persistent(cls, propname=None):
        if propname is not None:
            if not cls._properties.has_key(propname):
                raise ProgramError("propname %s is not defined in the Model.", propname)
            return cls._properties[propname].persistent
        for prop in cls._properties.values():
            if prop.persistent is True:
                return True
        return False
    
    def key(self):
        return self.get_keyvalue()
    
    def to_dict(self):
        tdt = {}
        pd = self._properties
        for key, prop in pd.items():
            if not key.startswith("_"):
                tdt[prop.get_label()] = prop.normalize_value(getattr(self, key))
        for key, value in self._extproperties.items():
            if not key.startswith("_"):
                tdt[key] = value
        tdt['key'] = self.get_keyvalue()
        return tdt
    
    def _normalize_property_value(self, name, value):
        if isinstance(value, Decimal):
            value = float(value)
        return value
    
    def _before_create(self, key=None, dbconn=None):
        """To be override by sub-class by need"""
        
    def _after_create(self, key=None, dbconn=None):
        """To be override by sub-class by need"""
    
    def create(self, key=None, dbconn=None):
        self._before_create(key=key)
        props = self.validate_props(persistent=True)
        if key == None:
            if self.is_auto_gen_key():
                key = self._get_dbconn(dbconn=dbconn).gen_key()
                props[self.get_keyname()] = key
                setattr(self, self.get_keyname(), key)
            elif self.get_keyvalue() is None:
                raise ProgramError("Key value can't be None when you create a new non-auto-gen-primary-key model %s.", self.get_modelname()) 
        else:
            props[self.get_keyname()] = key
            setattr(self, self.get_keyname(), key)
        key = self._get_dbconn(dbconn=dbconn).insert(self.get_modelname(), **props)
        self._after_create(key=key)
        return self
    
    def _before_update(self, dbconn=None):
        """To be override by sub-class by need"""
        
    def _after_update(self, dbconn=None):
        """To be override by sub-class by need"""
    
    def update(self, dbconn=None):
        self._before_update(dbconn=dbconn)
        props = self.validate_props(persistent=True)
        self._get_dbconn(dbconn=dbconn).update_by_key(self.get_modelname(), self.get_keyname(), self.get_keyvalue(), **props)
        self._after_update(dbconn=dbconn)
        return self
    
    def _before_delete(self, dbconn=None):
        """To be override by sub-class by need"""
        
    def _after_delete(self, dbconn=None):
        """To be override by sub-class by need"""
        
    def delete(self, dbconn=None):
        self._before_delete(dbconn=dbconn)
        self._get_dbconn(dbconn=dbconn).delete_by_key(self.get_modelname(), self.get_keyname(), self.get_keyvalue())
        self._after_delete(dbconn=dbconn)
        
    def validate_props(self, persistent=None):
        props = {}
        for pname, value in self.get_properties(persistent).items():
            if pname != self.get_keyname() and pname != self.DEFAULT_KEYNAME:
                pvalue = getattr(self, pname)
                if value.empty(pvalue) and value.required:
                    raise RequiredError(value.get_label())                
                value.validate(pvalue, model_instance=self)
                props[pname] = value.serialize_value(pvalue)
        
        self.get_property(self.get_keyname()).validate(self.get_keyvalue(), model_instance=self)
        
        props[self.get_keyname()] = self.get_keyvalue()
        return props
    
    @classmethod
    def all(cls, alias=None):
        if alias is None:
            alias = cls.get_modelname()
        return BaseQuery(cls, alias)
    
    @classmethod
    def get_by_key(cls, keyvalue, dbconn=None):
        dbconn = cls._get_dbconn(dbconn)
        result = dbconn.get_by_key(cls, keyvalue)
        return result
    
    @classmethod
    def _get_dbconn(cls, dbconn=None):
        if dbconn is None:
            dbconn = database.get_dbconn(cls)
        return dbconn
    
    def _is_entityinst(self):
        return self._entityinst
    
    # For query
    def _to_non_entityinst(self):
        self._entityinst = False
        return self
    
    def __str__(self):
        return "%s.%s[%s='%s']" % (self.meta_domain(), self.__class__.__name__, self.get_keyname(), self.key())
    
    def __repr__(self):
        options = ["%s='%s'" % (key, str(getattr(self, key))) for key in self.get_properties().keys()]
        options.append("ext_properties=%s" % self._extproperties)
        return "<%s.%s (%s)>" % (
            self.meta_domain(), self.__class__.__name__, ', '.join(options))

class BaseQuery(object):
    
    DESCENDING = 'desc'
    ASCENDING = 'asc'
    
    _QUERY_OPERATORS = ['ex', '<', '<=', '>', '>=', '=', '!=', 'in', 'not in', 'like', 'is', 'is not']
    _QUERY_FILTER_REGEX = re.compile(
    '^\s*([^\s]+)(\s+(%s)\s*)?$' % '|'.join(_QUERY_OPERATORS),
    re.IGNORECASE | re.UNICODE)
    
    _UPDATE_OPERATORS = ['inc', 'set', 'mul']
    _UPDATE_OPERATOR_REGEX = re.compile(
    '^\s*([^\s]+)(\s+(%s)\s*)?$' % '|'.join(_UPDATE_OPERATORS),
    re.IGNORECASE | re.UNICODE)
    
    DEFAULT_FETCH_LIMIT = 100000000

    def __init__(self, model_class, alias):
        if model_class == None or isinstance(model_class, BaseModel):
            raise ProgramError("model_class can't be None and non-sub-class-of-Model.")
        if alias == None or len(alias.strip()) == 0:
            raise ProgramError("alias can't be None or empty.")
        self._model_class = model_class
        self._model_name = model_class.get_modelname()
        self._model_alias = alias
        self._whats = []
        self._query_sets = []
        self._orderings = []
        self._groupings = None
        
        self._ql = None
        self._results = None
        self._update_sets = []
    
    def _get_dbconn(self, dbconn=None):
        if dbconn is None:
            dbconn = database.get_dbconn(self._model_class)
        return dbconn
    
    def get_model_class(self):
        return self._model_class
    
    # Return (model_name, alias)
    def get_model_name_alias(self):
        return (self._model_name, self._model_alias)
    
    def get_whats(self):
        if len(self._whats) == 0:
            model_class = self.get_model_class()
            model_alias = self.get_model_name_alias()[1]
            for key in model_class.get_properties(persistent=True).keys():
                if key != self.get_model_class().DEFAULT_KEYNAME: 
                    self.what("%s.%s" % (model_alias, key), key)
                    
            if (model_class.get_keyname() == model_class.DEFAULT_KEYNAME):
                self.what("%s.%s" % (model_alias, model_class.DEFAULT_KEYNAME))
        return self._whats
    
    def get_update_sets(self):
        return self._update_sets
       
    def get_query_sets(self):
        return self._query_sets
    
    def get_orderings(self):
        return self._orderings
    
    def get_groupings(self):
        return self._groupings
        
    # Return ql
    def get_ql(self):
        return self._ql
    
        
    def filter(self, property_operator, value, wrapper=True, logic="and", parenthesis=None, dot=False, replace=False):
        """
            logic means the logic relationship with the preceding criteria. for example,
                filter("a =",1) and  filter("b =",2, logic="or") will formulate the query, 
                a = 1 or logic = 2 in SQL database  
                {"or": [{"a":{'$eq': 1}},{"b":{'$eq': 2}}] } in Mongodb
            wrapper = True means value will be processed by the method dbclient._wrap_query_parameter 
        """
        match = self._QUERY_FILTER_REGEX.match(property_operator)
        prop_name = ""
        logic = logic.lower()
        if logic != 'and' and logic != 'or':
            raise ProgramError("logic %s is not and AND or" , logic)
        if parenthesis is not None and parenthesis not in ('(' , '((', '(((', '((((', '(((((') and parenthesis not in (")" , "))", ")))", "))))", ")))))"):
            raise ProgramError("parenthesis %s is not ( or ) or the string with multiple ( or )" , parenthesis)
        if match != None and match.group(1) is not None:
            prop_name = match.group(1)
        else:
            raise ProgramError('the property operator %s includes the illegal operator' , property_operator)
        
        if match.group(3) is not None:
            operator = match.group(3)
        else:
            operator = '='
            
        if property_operator != 'ex ex' and self._model_class.is_persistent():
            pname = prop_name if "." not in prop_name else prop_name.split(".")[1]
            if not self._model_class.is_persistent(pname):
                raise ProgramError('the property %s is not the persistent property in model %s ' , pname, self._model_class.__name__)
            
            prop = getattr(self._model_class, pname)
            if value != None and operator != 'in' and operator != 'not in' and wrapper and not isinstance(value, prop.data_type):
                raise ProgramError('the value %s of the property %s  is not the type %s ' , str(value), pname, str(prop.data_type))     
        
        if operator.lower() == 'in' or operator.lower() == 'not in':
            if wrapper is True:
                if not isinstance(value, (list, tuple)):
                    raise ProgramError('Argument to the "in" operator must be a list or wrapper=False')
                value = [self._normalize_query_parameter(v) for v in value]
            else:
                value = value
        else:
            if isinstance(value, (list, tuple)):
                raise ProgramError('Filtering on lists is not supported for the operator %s', operator)
            else:
                value = self._normalize_query_parameter(value)
        if value is None:
            operator = "is" if operator in ('=', 'is') else 'is not'
        self._append_query_set(prop_name, operator, value, wrapper, logic, parenthesis, dot, replace)
        return self
    
    def filter_x(self, filters, parenthesis_left=None, parenthesis_right=None, logic="and"):
        """
            filters must be a list with dict as the element. for example,
            [
                {'property_op':'f_int =', 'value':1},
                 {'property_op':'f_str =', 'value':'abced', 'parenthesis':'('}, 
                 {'property_op':'f_str =', 'value':'xfg', 'parenthesis':')', 'logic':'or'}
             ]
            logic means the logic between filters with the preceding criteria. 
        """
        i = 0
        for filter_dic in filters:
            if not filter_dic.has_key('property_op'):
                raise ProgramError("filter dict does not include parameter 'property_op' ")
            if not filter_dic.has_key('value'):
                raise ProgramError("filter dict does not include parameter 'value' ")
            property_op = filter_dic['property_op']
            value = filter_dic['value']
            wrapper = filter_dic['wrapper'] if filter_dic.has_key('wrapper') else True
            logical = filter_dic['logic'] if filter_dic.has_key('logic') else "and"
            parenthesis = filter_dic['parenthesis'] if filter_dic.has_key('parenthesis') else None
            if i == 0:
                logical = logic
                parenthesis = parenthesis if parenthesis_left is None else "(" if parenthesis is None else parenthesis + "("
            if i == len(filters) - 1:
                parenthesis = parenthesis if parenthesis_right is None else ")" if parenthesis is None else parenthesis + ")"
            dot = filter_dic['dot'] if filter_dic.has_key('dot') else False
            replace = filter_dic['replace'] if filter_dic.has_key('replace') else False
            self.filter(property_op, value, wrapper=wrapper, logic=logical, parenthesis=parenthesis, dot=dot, replace=replace)
            i += 1
        return self
        
    def has_filter(self, propname, operator=None):
        for query_set in self._query_sets:
            if query_set[0] == propname and (operator == None or query_set[1] == operator):
                return True
        return False
    
    def order(self, prop):
        order = BaseQuery.ASCENDING
        if prop.startswith('-'):
            prop = prop[1:]
            order = BaseQuery.DESCENDING
        self._orderings.append((prop, order))
        return self
    
    def what(self, name, alias=None):
        if typeutils.str_is_empty(alias):
            alias = name if "." not in name else name.split(".")[1]
        self._whats.append((name, alias))
        return self
    
    def group(self, *args):
        self._groupings = args
        return self
    
    def ql(self, *args):
        """
            for example: 
            *args = "SELECT * FROM foo WHERE x = $x", dict(x='f')
                or
            *args = {"grades.score": {"$lt": 8}}, {'_id':1, 'score':0}
        """
        self._ql = args
        return self
    
    
    def fetch(self, limit=DEFAULT_FETCH_LIMIT, offset=0, paging=False, metadata=None, mocallback=None, dbconn=None):
        """
             metadata is directory and the key, value is prop name, subclass of Property. eg. {'f_bool', dao.BooleanProperty()}
        """
        if self._results == None:
            self._results = self._get_dbconn(dbconn=dbconn).find(self, limit, offset, paging=paging, metadata=metadata, mocallback=mocallback)
        return self._results
    
    def find_one_and_update(self, new=False, metadata=None, mocallback=None, dbconn=None):
        """
            Modifies and returns a single model.
            query: filter method is used to select models, sort method is used to decide which one is updated. 
                    what method is subset of fields to return. set method is the value specifications to modify the selected record.   
            new : When true,  returns the modified than the original. 
            update: value specifications to modify the record
        """
        return self._get_dbconn(dbconn=dbconn).find_one_and_update(self, new=new, metadata=metadata, mocallback=mocallback)
    
    def find_one_and_delete(self, metadata=None, mocallback=None, dbconn=None):
        """
            Delete and returns the deleted model.
            query: filter method is used to select models, sort method is used to decide which one is deleted. 
                    what method is subset of fields to return.   
        """
        return self._get_dbconn(dbconn=dbconn).find_one_and_delete(self, metadata=metadata, mocallback=mocallback)
    
    def get(self, metadata=None, mocallback=None, dbconn=None):
        if self._results == None:
            self._results = self.fetch(1, metadata=metadata, mocallback=mocallback, dbconn=dbconn)
        if len(self._results) > 0:
            return self._results[0]
        else:
            return None
        
    def count(self, dbconn=None):
        quantity = 0
        if self._results is None:
            quantity = self._get_dbconn(dbconn=dbconn).count(self)
        else:
            quantity = len(self._results)
        return quantity
        
    def update(self, dbconn=None):
        result = self._get_dbconn(dbconn=dbconn).update_multiple(self)
        return result
    
    def delete(self, dbconn=None):
        results = self._get_dbconn(dbconn=dbconn).delete_multiple(self)
        return results
   
    def set(self, property_operator, value):
        """
           property_operator is the two phrases link by space. the pattern is like like 'a $inc'.
           Support operator is as below:
           inc    Increments the value of the field by the specified amount.
           mul    Multiplies the value of the field by the specified amount.   
           set    Sets the value of a field in a record.                    
        """
        match = self._UPDATE_OPERATOR_REGEX.match(property_operator)
        propname = ""
        if match != None and match.group(1) is not None:
            propname = match.group(1)
        else:
            raise ProgramError('the property operator %s includes the illegal operator' , property_operator)
        if not self._model_class.get_properties().has_key(propname):
            raise ProgramError("propname %s is not a property of model %s" % (propname, self._model_class))
        
        if not self._model_class.is_persistent(propname):
            raise ProgramError("propname %s is not a persistent propperty." % propname)
        
        if match.group(3) is not None:
            operator = match.group(3)
        else:
            operator = 'set'
        
        prop = self._model_class.get_properties()[propname]    
        value = prop.validate(value, self)
        value = prop.serialize_value(value)
        value = self._normalize_query_parameter(value)
        self._update_sets.append((propname, operator, value))       
        
    def clear(self):
        self._results = None
        self._query_sets = []
        self._orderings = []
        self._groupings = None
    
    def _append_query_set(self, propname, operator, value, wrapper, logic, parenthesis, dot, replace):
        if replace is True:
            query_sets = []
            if len(self._query_sets) == 0:
                self._query_sets.append((propname, operator, value, wrapper, logic, parenthesis, dot))
            else:
                for query_set in self._query_sets:
                    if query_set[0] == propname:
                        query_set_1 = (propname, operator, value, wrapper, logic, parenthesis, dot)
                        query_sets.append(query_set_1)
                    else:
                        query_sets.append(query_set)
                self._query_sets = query_sets
        else:
            self._query_sets.append((propname, operator, value, wrapper, logic, parenthesis, dot))
            
        
    def _normalize_query_parameter(self, value):
        if isinstance(value, datetime.datetime):
            value = value.replace(tzinfo=None)
        elif (isinstance(value, datetime.date) and not isinstance(value, datetime.datetime)):
            value = datetime.date(value.year, value.month, value.day)
        elif isinstance(value, datetime.time):
            value = datetime.datetime(1970, 1, 1, value.hour, value.minute, value.second, value.microsecond)
                
        return value
    
class Model(BaseModel):
    
    NULL_USER_ID = "NUL"
    SYS_USER_ID = "SYS"
    
    @classmethod
    def meta_domain(cls):
        """To be implemented by sub-class"""
        raise NotImplementedError("Model.meta_domain")
    
    created_time = DateTimeProperty("createdTime", required=True, auto_utcnow=True)
    modified_time = DateTimeProperty("modifiedTime", required=True, auto_utcnow=True)
    created_by = StringProperty("creatorKey", required=True)
    modified_by = StringProperty("modifierKey", required=True)
    row_version = IntegerProperty("rowVersion", required=True, default=1)
    
    def __init__(self, entityinst=False, **kwds):
        super(Model, self).__init__(entityinst=entityinst, **kwds)
        
    @classmethod
    def all(cls, alias=None):
        if alias is None:
            alias = cls.get_modelname()
        return Query(cls, alias=alias)
    
    def delete(self, deleted_by, dbconn=None):
        if typeutils.str_is_empty(deleted_by):
            deleted_by = self.NULL_USER_ID
        BaseModel.delete(self, dbconn=dbconn)
        return self.get_keyvalue()
    
    def create(self, created_by, key=None, dbconn=None):
        if typeutils.str_is_empty(created_by):
            created_by = self.NULL_USER_ID
        self.created_by = created_by
        self.modified_by = created_by
        self.created_time = typeutils.utcnow()
        self.modified_time = typeutils.utcnow()
        self.row_version = 1
        return BaseModel.create(self, key=key, dbconn=dbconn)
    
    def update(self, modified_by, dbconn=None):
        if typeutils.str_is_empty(modified_by):
            modified_by = self.NULL_USER_ID
        lastmodel = self.get_by_key(self.get_keyvalue())
        if lastmodel.row_version != self.row_version:
            raise DataExpiredError()
        self.update_timestamp(modified_by)        
        newmodel = BaseModel.update(self, dbconn=dbconn)
        from ssguan.commons import loggingg
        loggingg.add_mclog(lastmodel, newmodel, modified_by)
        return newmodel
        
    def update_timestamp(self, modified_by):
        if typeutils.str_is_empty(modified_by):
            modified_by = self.NULL_USER_ID
        self.modified_by = modified_by
        self.modified_time = typeutils.utcnow()
        self.row_version += 1
     
    def to_dict(self, tzstr=typeutils.tz_utc()):
        tdt = BaseModel.to_dict(self)
       
        ctp = self.get_property("created_time")
        ctp.fmt = typeutils.datesecond_format()
        created_time = typeutils.utc_to_local(self.created_time, tzstr)
        tdt["createdTime"] = ctp.to_string(created_time)
        
        mtp = self.get_property("modified_time")
        mtp.fmt = typeutils.datesecond_format()
        modified_time = typeutils.utc_to_local(self.modified_time, tzstr)
        tdt["modifiedTime"] = mtp.to_string(modified_time)
        
        return tdt
    
            
class Query(BaseQuery):
    
    def update(self, modified_by, dbconn=None):
        if typeutils.str_is_empty(modified_by):
            modified_by = self._model_class.NULL_USER_ID
        self.set("modified_time", datetime.datetime.utcnow())
        self.set("modified_by", modified_by)
        self.set("row_version inc", 1)
        for upfield in self._update_sets:
            if self._model_class.get_properties(True)[upfield[0]].logged:
                raise ProgramError("Query.update doesn't support to update the logged property %r" % upfield[0])
        result = BaseQuery.update(self, dbconn=dbconn)
        return result
    
    def delete(self, deleted_by, dbconn=None):
        if typeutils.str_is_empty(deleted_by):
            deleted_by = self._model_class.NULL_USER_ID
        result = BaseQuery.delete(self, dbconn=dbconn)
        return result

    def find_one_and_update(self, modified_by, new=False, metadata=None, mocallback=None, dbconn=None):
        self.set("modified_time", datetime.datetime.utcnow())
        if typeutils.str_is_empty(modified_by):
            modified_by = Model.NULL_USER_ID
        self.set("modified_by", modified_by)
        return BaseQuery.find_one_and_update(self, new=new, metadata=metadata, mocallback=mocallback, dbconn=dbconn)
    
    def find_one_and_delete(self, modified_by, metadata=None, mocallback=None, dbconn=None):
        self.set("modified_time", datetime.datetime.utcnow())
        if typeutils.str_is_empty(modified_by):
            modified_by = Model.NULL_USER_ID
        self.set("modified_by", modified_by)
        return BaseQuery.find_one_and_delete(self, metadata=metadata, mocallback=mocallback, dbconn=dbconn)

class DataExpiredError(Error):
    def __init__(self):
        super(DataExpiredError, self).__init__("The local data is expired, please refresh data or UI after reloading latest data from server.")
    
    @property
    def code(self):
        return 1010      

