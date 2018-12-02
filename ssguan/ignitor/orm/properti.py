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

from ssguan.ignitor.base.error import RequiredError, ChoiceError, LengthError, \
    TypeIntError, TypeFloatError, TypeBoolError, TypeDatetimeError, \
    TypeDateError, TypeListError, TypeDictError
from ssguan.ignitor.orm.validator import Validator
from ssguan.ignitor.utility import kind
from ssguan.ignitor.base.error import  ProgramError


class Property(object):

    def __init__(self, name=None, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        self._name = name
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
        """
            get the name which is defined in error message
        """
        return self._name
    
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
    
    data_type = (str)
    
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
    def __init__(self, length=80, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(StringProperty, self).__init__(persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)
        self.length = length

    def validate(self, value, model_instance):
        value = super(StringProperty, self).validate(value, model_instance)
        if value is not None and not isinstance(value, str):
            value = str(value)
        if value is not None and len(value) > self.length:
            raise LengthError(self.get_label(), 0, self.length)
        return value
    
    data_type = (str)
    
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
        return kind.str_is_empty(value)

class IntegerProperty(Property):
    
    def __init__(self, persistent=True, length=11, default=None, required=False, validator=None, choices=None, logged=False):
        super(IntegerProperty, self).__init__(persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)
        self.length = length
    
    def validate(self, value, model_instance):
        value = super(IntegerProperty, self).validate(value, model_instance)
        if value is None:
            return value
        
        if isinstance(value, str):
            if not kind.str_is_int(value):
                raise TypeIntError(self.get_label())
            else:
                value = int(value)
        
        if not isinstance(value, (int)) or isinstance(value, bool):
            raise TypeIntError(self.get_label())
        if (len(str(value)) > self.length):
            raise LengthError(self.get_label(), 0, self.length)
        if value < -0x8000000000000000 or value > 0x7fffffffffffffff:
            raise ProgramError('Property %s must fit in 64 bits' % self._name)
        return value

    def empty(self, value):    
        return value is None
    
    data_type = (int)
    def db_data_type(self):
        return "int(%d)" % self.length 
    
    def normalize_value(self, value):
        return value if type(value) is int else kind.str_to_int(value)

class FloatProperty(Property):
    
    def __init__(self, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(FloatProperty, self).__init__(persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        value = super(FloatProperty, self).validate(value, model_instance)
        
        if isinstance(value, str):
            if not kind.str_is_float(value):
                raise TypeFloatError(self.get_label())
            else:
                value = float(value)
        
        if value is not None and not isinstance(value, float):
            raise TypeFloatError(self.get_label())
        return value

    def empty(self, value):
        return value is None
    
    data_type = (float)
    def db_data_type(self):
        return "float"
    
    def normalize_value(self, value):
        return value if type(value) is float else kind.str_to_float(value)

class BooleanProperty(Property):
    
    def __init__(self, persistent=True, required=True, default=False, validator=None, logged=False):
        super(BooleanProperty, self).__init__(persistent=persistent, default=default, required=required, validator=validator, logged=logged)

    def validate(self, value, model_instance):
        value = super(BooleanProperty, self).validate(value, model_instance)
        if value is not None and not isinstance(value, bool):
            raise TypeBoolError(self.get_label())
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

    def __init__(self, persistent=True, auto_utcnow=False, required=False, validator=None, fmt=None, logged=False):
        super(DateTimeProperty, self).__init__(persistent=persistent, default=None, required=required, validator=validator, logged=logged)
        self.auto_now = auto_utcnow
        self.fmt = fmt

    def validate(self, value, model_instance):
        value = super(DateTimeProperty, self).validate(value, model_instance)
        
        if isinstance(value, str):
            if not kind.str_is_datetime(value, fmt=self.fmt):
                raise TypeDatetimeError(self.get_label())
            else:
                value = kind.str_to_datetime(value, fmt=self.fmt)
                value = kind.local_to_utc(value)
        
        if value and not isinstance(value, self.data_type):
            raise TypeDatetimeError(self.get_label(), self.fmt)
        return value

    def default_value(self):
        if self.auto_now:
            now = self.utcnow()
            return now
        else:
            return Property.default_value(self)

    @staticmethod
    def utcnow():
        return kind.utcnow()
    
    data_type = (datetime.datetime)
    def db_data_type(self):
        return "datetime"
    
    def serialize_value(self, value):
        if value is not None:
            value = kind.local_to_utc(value)
            value = value.replace(tzinfo=None)
            value = kind.datetime_floor(value)
        return value
    
    def normalize_value(self, value):
        if not isinstance(value, datetime.datetime):
            value = kind.str_to_datetime(value, fmt=self.fmt)
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=kind.tz_utc())
        return value
        
    def to_string(self, value):
        return value if value is None else self.normalize_value(value).strftime(self.fmt)

class DateProperty(Property):
    
    def __init__(self, persistent=True, auto_utctoday=False, required=False, validator=None, fmt=None, logged=False):
        super(DateProperty, self).__init__(persistent=persistent, default=None, required=required, validator=validator, logged=logged)
        self.auto_today = auto_utctoday
        self.fmt = fmt

    def validate(self, value, model_instance):
        value = super(DateProperty, self).validate(value, model_instance)
        
        if isinstance(value, str):
            if not kind.str_is_date(value, fmt=self.fmt):
                raise TypeDateError(self.get_label())
            else:
                value = kind.str_to_date(value, fmt=self.fmt)
        if isinstance(value , datetime.datetime):
            value = kind.datetime_to_date(value)
        if value and not isinstance(value, self.data_type):
            raise TypeDateError(self.get_label(), self.fmt)
        return value

    def default_value(self):
        if self.auto_today:
            today = self.utctoday()
            return today
        else:
            return Property.default_value(self)
    
    @staticmethod
    def utctoday():
        return kind.utctoday()
    
    data_type = datetime.date
    def db_data_type(self):
        return "date"
    
    def serialize_value(self, value):
        if isinstance(value, datetime.datetime):
            return kind.datetime_to_date(value)
        return value
    
    def normalize_value(self, value):
        if isinstance(value, datetime.datetime):
            return kind.datetime_to_date(value)
        elif isinstance(value, datetime.date):
            return value
        else:
            return kind.str_to_date(value, fmt=self.fmt)
        
    def to_string(self, value):
        return value if value is None else self.normalize_value(value).strftime(self.fmt)

class TimezoneProperty(StringProperty):
    
    def __init__(self, default=None, logged=False):
        super(TimezoneProperty, self).__init__(required=True, length=40, default=default, logged=logged)

    def serialize_value(self, value):
        return str(value)
    
    def normalize_value(self, value):
        return kind.tz_timezone(value)

class ListProperty(StringProperty):
    def __init__(self, length=4096, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(ListProperty, self).__init__(length=length, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        if value is not None and type(value) != list:
            raise TypeListError(self.get_label())
        value1 = self.serialize_value(value)
        if value1 is not None and len(value1) > self.length:
            raise LengthError(self.get_label(), 0, self.length)
        return value
    
    def serialize_value(self, value):
        if value is None:
            return value
        else:
            return kind.obj_to_json(value)
    
    def normalize_value(self, value):
        value = self.to_string(value)
        if kind.str_is_empty(value):
            return None
        else:
            return kind.json_to_object(value)


class DictProperty(StringProperty):
    def __init__(self, length=4096, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(DictProperty, self).__init__(length=length, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        if value is not None and type(value) != dict:
            raise TypeDictError(self.get_label())
        value1 = self.serialize_value(value)
        if value1 is not None and len(value1) > self.length:
            raise LengthError(self.get_label(), 0, self.length)
        return value
    
    def serialize_value(self, value):
        if value is None:
            return value
        else:
            return kind.obj_to_json(value)
    
    def normalize_value(self, value):
        value = self.to_string(value)
        if kind.str_is_empty(value):
            return None
        else:
            return kind.json_to_object(value)

class ObjectProperty(StringProperty):
    def __init__(self, length=1048576, persistent=True, default=None, required=False, validator=None, choices=None, logged=False):
        super(ObjectProperty, self).__init__(length=length, persistent=persistent, default=default, required=required, validator=validator, choices=choices, logged=logged)

    def validate(self, value, model_instance):
        value1 = self.serialize_value(value)
        if value1 is not None and len(value1) > self.length:
            raise LengthError(self.get_label(), 0, self.length)
        return value
    
    def serialize_value(self, value):
        if value is None:
            return None
        else:
            return kind.obj_to_pickle(value)
    
    def normalize_value(self, value):
        value = self.to_string(value)
        if kind.str_is_empty(value):
            return None
        else:
            return kind.pickle_to_obj(value)
        

        


