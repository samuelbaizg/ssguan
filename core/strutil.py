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
import re


def to_bool(value, default=False):
    if is_empty(value) or not is_bool(value):
        return default
    value = str(value)
    if value.lower() in ('true', 'yes', '1', 'y'):
        return True
    else:
        return False

def to_date(value, fmt=None, default=None):
    fmt = '%Y-%m-%d' if fmt is None else fmt
    if is_empty(value) or not is_date(value, fmt=fmt):
        return default
    else:
        value = str(value)
        dt = datetime.datetime.strptime(value, fmt)
        return datetime.date(dt.year,dt.month,dt.day)
        
def to_datetime(value, fmt=None, default=None):
    fmt = '%Y-%m-%d %H:%M:%S' if fmt is None else fmt
    if is_empty(value) or not is_datetime(value, fmt=fmt):
        return default
    else:
        value = str(value)
        return datetime.datetime.strptime(value, fmt)

def to_int(value, default=None):
    if is_empty(value) or not is_int(value):
        return default
    else:
        value = str(value)
        return int(value)
    
def to_float(value, default=None):
    if is_empty(value) or (not is_int(value) and not is_float(value)):
        return default
    else:
        value = str(value)
        return float(value)

def to_list(value, default=None):
    if is_empty(value) or (not is_list(value) and not is_tuple(value)):
        return default
    else:
        value = value[1:-1]
        value = value.split(",")
        return value

def to_object(value, default=None, strict=True, fmt=None):
    value = str(value)
    if is_empty(value):
        return default
    if is_list(value) or is_tuple(value):
            value = to_list(value, default)
    elif not strict and is_bool(value):
        value = to_bool(value, default)
    elif strict and value.lower() == 'true':
        value = True
    elif strict and value.lower() == 'false':
        value = False
    elif is_int(value):
        value = to_int(value, default)
    elif is_float(value):
        value = to_float(value, default)
    elif is_date(value, fmt):
        value = to_date(value, fmt, default)
    elif is_datetime(value, fmt):
        value = to_datetime(value, fmt, default)
       
    return value

def to_str(value, default=None, fmt=None):
    if value is None:
        return default
    if type(value) == list or type(value) == tuple:
        value = "[%s]" % ",".join(map(str,value))
    elif is_date(value, fmt):
        value = value.strftime(fmt)
    elif is_datetime(value, fmt):
        value = value.strftime(fmt)
    else:
        value = str(value)
    return value

def replce_html_entities(value):
    if is_empty(value):
        return value
    value = str(value)
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    return value

def is_int(value):
    reg = re.compile("^[-]?\d+?$")
    if is_empty(value):
        return False
    else:
        try:
            value = str(value)
            result = reg.match(value)
            if result != None:
                return True
            else:
                return False
        except:
            return False

def is_float(value):
    reg = re.compile("^[-]?\d+?\.\d+?$")
    if is_empty(value):
        return False
    else:
        try:
            value = str(value)
            result = reg.match(value)
            if result != None:
                return True
            else:
                return False
        except:
            return False

def is_date(value, fmt=None):
    reg = re.compile("[\d]{4}(\-|\/|\.)[\d]{1,2}(\-|\/|\.)[\d]{1,2}")
    if is_empty(value):
        return False
    else:
        try:
            value = str(value)
            result = reg.match(value)
            if result != None:
                return True
            else:
                return False
        except:
            return False

def is_datetime(value, fmt=None):
    reg = re.compile("[\d]{4}(\-|\/|\.)[\d]{1,2}(\-|\/|\.)[\d]{1,2} [\d]{1,2}:[\d]{1,2}[ AM,PM]{0,2}")
    if is_empty(value):
        return False
    else:
        try:
            value = str(value)
            result = reg.match(value)
            if result != None:
                return True
            else:
                return False
        except:
            return False

def is_bool(value):
    if is_empty(value):
        return False
    value = str(value)
    if value.lower() in ('true', 'yes', '1'):
        return True
    elif value.lower() in ('false', 'no', '0'):
        return True
    else:
        return False
    
def is_empty(value):
    if value == None:
        return True
    else:
        if isinstance(value, str) or isinstance(value, unicode):
            value = str(value).strip()
            return  len(value) == 0
        else:
            return False

def is_list(value):
    if is_empty(value):
        return False
    value = str(value)
    if value.startswith("[") and value.endswith("]"):
        return True
    else:
        return False
    
def is_tuple(value):
    if is_empty(value):
        return False
    value = str(value)
    if value.startswith("(") and value.endswith(")"):
        return True
    else:
        return False
