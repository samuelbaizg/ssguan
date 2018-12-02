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
import __builtin__
import base64
from calendar import timegm
import calendar

from datetime import tzinfo, timedelta
import datetime
from hashlib import md5, sha256
import itertools
import json
import re
import sys

import time
import traceback
import uuid

import pytz
from six import iteritems
import six
import tzlocal

import cPickle as Pickle


def _str_strips(direction, text, remove):
    if isinstance(remove, iters):
        for subr in remove:
            text = _str_strips(direction, text, subr)
        return text
    
    if direction == 'l': 
        if text.startswith(remove): 
            return text[len(remove):]
    elif direction == 'r':
        if text.endswith(remove):   
            return text[:-len(remove)]
    else: 
        raise ValueError, "Direction needs to be r or l."
    return text

def str_rstrips(text, remove):
    """
    removes the string `remove` from the right of `text`

        >>> rstrips("foobar", "bar")
        'foo'
    
    """
    return _str_strips('r', text, remove)

def str_lstrips(text, remove):
    """
    removes the string `remove` from the left of `text`
    
        >>> lstrips("foobar", "foo")
        'bar'
        >>> lstrips('http://foo.org/', ['http://', 'https://'])
        'foo.org/'
        >>> lstrips('FOOBARBAZ', ['FOO', 'BAR'])
        'BAZ'
        >>> lstrips('FOOBARBAZ', ['BAR', 'FOO'])
        'BARBAZ'
    
    """
    return _str_strips('l', text, remove)

def str_strips(text, remove):
    """
    removes the string `remove` from the both sides of `text`

        >>> str_strips("foobarfoo", "foo")
        'bar'
    
    """
    return str_rstrips(str_lstrips(text, remove), remove)

def str_numify(string):
    """
    Removes all non-digit characters from `string`.
    
        >>> numify('800-555-1212')
        '8005551212'
        >>> numify('800.555.1212')
        '8005551212'
    
    """
    return ''.join([c for c in str(string) if c.isdigit()])

def str_denumify(string, pattern):
    """
    Formats `string` according to `pattern`, where the letter X gets replaced
    by characters from `string`.
    
        >>> str_denumify("8005551212", "(XXX) XXX-XXXX")
        '(800) 555-1212'
    
    """
    out = []
    for c in pattern:
        if c == "X":
            out.append(string[0])
            string = string[1:]
        else:
            out.append(c)
    return ''.join(out)

def str_commify(n):
    """
    Add commas to an integer `n`.

        >>> commify(1)
        '1'
        >>> commify(123)
        '123'
        >>> commify(1234)
        '1,234'
        >>> commify(1234567890)
        '1,234,567,890'
        >>> commify(123.0)
        '123.0'
        >>> commify(1234.5)
        '1,234.5'
        >>> commify(1234.56789)
        '1,234.56789'
        >>> commify('%.2f' % 1234.5)
        '1,234.50'
        >>> commify(None)
        >>>

    """
    if n is None: return None
    n = str(n)
    if '.' in n:
        dollars, cents = n.split('.')
    else:
        dollars, cents = n, None

    r = []
    for i, c in enumerate(str(dollars)[::-1]):
        if i and (not (i % 3)):
            r.insert(0, ',')
        r.insert(0, c)
    out = ''.join(r)
    if cents:
        out += '.' + cents
    return out

def str_dateify(datestring):
    """
    Formats a numified `datestring` properly.
    """
    return str_denumify(datestring, "XXXX-XX-XX XX:XX:XX")

def str_to_bool(value, default=False):
    if str_is_empty(value) or not str_is_bool(value):
        return default
    value = str(value)
    if value.lower() in ('true', 'yes', '1', 'y'):
        return True
    else:
        return False

def str_to_date(value, fmt=None, default=None):
    fmt = date_format() if fmt is None else fmt
    if str_is_empty(value) or not str_is_date(value, fmt=fmt):
        return default
    else:
        value = str(value)
        dt = datetime.datetime.strptime(value, fmt)
        return datetime.date(dt.year, dt.month, dt.day)

     
def str_to_datetime(value, fmt=None, default=None):
    fmt = datetime_format() if fmt is None else fmt
    if str_is_empty(value) or not str_is_datetime(value, fmt=fmt):
        return default
    else:
        value = str(value)
        dt = datetime.datetime.strptime(value, fmt)
        dt = dt.replace(tzinfo=tz_utc())
        return dt

def str_to_int(value, default=None):
    if str_is_empty(value) or not str_is_int(value):
        return default
    else:
        value = str(value)
        return int(value)

def str_to_float(value, default=None):
    if str_is_empty(value) or (not str_is_int(value) and not str_is_float(value)):
        return default
    else:
        value = str(value)
        return float(value)
    
def str_to_list(value, default=None):
    if str_is_empty(value) or (not str_is_list(value) and not str_is_tuple(value)):
        return default
    else:
        value = json_to_object(value)
        return value

def str_to_dict(value, default=None):
    if str_is_empty(value) or (not str_is_dict(value) and not str_is_dict(value)):
        return default
    else:
        return json_to_object(value)
    
def str_to_object(value, default=None, strict=True, fmt=None):
    value = str(value)
    if str_is_empty(value):
        return default
    if str_is_list(value) or str_is_tuple(value):
            value = str_to_list(value, default)
    elif str_is_dict(value):
            value = str_to_dict(value, default)
    elif not strict and str_is_bool(value):
        value = str_to_bool(value, default)
    elif strict and value.lower() == 'true':
        value = True
    elif strict and value.lower() == 'false':
        value = False
    elif str_is_int(value):
        value = str_to_int(value, default)
    elif str_is_float(value):
        value = str_to_float(value, default)
    elif str_is_datetime(value, fmt):
        value = str_to_datetime(value, fmt, default)
    elif str_is_date(value, fmt):
        value = str_to_date(value, fmt, default)
    return value

def obj_to_str(value, default=None, fmt=None):
    if value is None:
        return default
    if type(value) == list or type(value) == tuple:
        value = obj_to_json(value)
    elif type(value) == dict:
        value = obj_to_json(value)
    elif type(value) == datetime.datetime or type(value) == datetime.date:
        value = datetime_to_str(value, fmt)
    else:
        value = str(value)
    return value

def obj_to_pickle(value):
    return Pickle.dumps(value)

def pickle_to_obj(value):
    return Pickle.loads(str(value))

def str_replce_html_entities(value):
    if str_is_empty(value):
        return value
    value = str(value)
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    return value

def str_is_int(value):
    reg = re.compile("^[-]?\d+?$")
    if str_is_empty(value):
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

def str_is_float(value):
    reg = re.compile("^[-]?\d+?\.\d+?$")
    if str_is_empty(value):
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

def str_is_date(value, fmt=None):
    fmt = date_format() if fmt is None else fmt
    try:
        time.strptime(value, fmt)
        return True
    except:
        return False

def str_is_datetime(value, fmt=None):
    fmt = datetime_format() if fmt is None else fmt
    try:
        time.strptime(value, fmt)
        return True
    except:
        return False
        
def str_is_bool(value):
    if str_is_empty(value):
        return False
    value = str(value)
    if value.lower() in ('true', 'yes', '1'):
        return True
    elif value.lower() in ('false', 'no', '0'):
        return True
    else:
        return False
    
def str_is_empty(value):
    if value == None:
        return True
    else:
        if isinstance(value, str) or isinstance(value, unicode):
            value = str(value).strip()
            return  len(value) == 0
        else:
            return False
        
def str_is_list(value):
    if str_is_empty(value):
        return False
    value = str(value)
    if value.startswith("[") and value.endswith("]"):
        return True
    else:
        return False
    
def str_is_tuple(value):
    if str_is_empty(value):
        return False
    value = str(value)
    if value.startswith("(") and value.endswith(")"):
        return True
    else:
        return False
    
def str_is_dict(value):
    if str_is_empty(value):
        return False
    value = str(value)
    if value.startswith("{") and value.endswith("}") and ":" in value:
        return True
    else:
        return False
    
def int_nthstr(n):
    """
    Formats an ordinal.
    Doesn't handle negative numbers.

        >>> nthstr(1)
        '1st'
        >>> nthstr(0)
        '0th'
        >>> [nthstr(x) for x in [2, 3, 4, 5, 10, 11, 12, 13, 14, 15]]
        ['2nd', '3rd', '4th', '5th', '10th', '11th', '12th', '13th', '14th', '15th']
        >>> [nthstr(x) for x in [91, 92, 93, 94, 99, 100, 101, 102]]
        ['91st', '92nd', '93rd', '94th', '99th', '100th', '101st', '102nd']
        >>> [nthstr(x) for x in [111, 112, 113, 114, 115]]
        ['111th', '112th', '113th', '114th', '115th']

    """
    
    assert n >= 0
    if n % 100 in [11, 12, 13]: return '%sth' % n
    return {1: '%sst', 2: '%snd', 3: '%srd'}.get(n % 10, '%sth') % n

def daysofmonth(year, month):
        return calendar.monthrange(year, month)[1]
    
def tz_timezone(tz=None):
    """
    Interprets an object as a timezone.
    :param tz str|tzinfo
    :rtype: tzinfo  return localzone if tzinfo is None
    """
    if tz is None:
        return tzlocal.get_localzone()
    elif isinstance(tz, six.string_types):
        return pytz.timezone(tz)
    if isinstance(tz, tzinfo):
        if not hasattr(tz, 'localize') or not hasattr(tz, 'normalize'):
            raise TypeError('Only timezones from the pytz library are supported')
        if tz.zone == 'local':
            raise ValueError(
                'Unable to determine the name of the local timezone -- you must explicitly '
                'specify the name of the local timezone. Please refrain from using timezones like '
                'EST to prevent problems with daylight saving time. Instead, use a locale based '
                'timezone name (such as Europe/Helsinki).')
        return tz
    if tz is not None:
        raise TypeError('Expected tzinfo, got %s instead' % tz.__class__.__name__)

def tz_localzone():
    return tz_timezone(tz=None)

def tz_utc():
    return pytz.utc

def tz_china():
    """
    :rtype tzinfo
    """
    return tz_timezone("Asia/Shanghai")

def localnow(tz=None):
    tz = tz_timezone(tz)
    now = utcnow()    
    local = utc_to_local(now, tz)
    return local

def localtoday(tz=None):
    local = localnow(tz=tz)
    return datetime_to_date(local)

def utcnow():
    utcnow = datetime.datetime.utcnow()
    utcnow = utcnow.replace(tzinfo=tz_utc())
    return utcnow

def utctoday():
    now = utcnow()
    return datetime.date(now.year, now.month, now.day)
   
def local_to_utc(localdt):
    """
        if tzinfo is None of localdt, localzone is used for the conversion.
    """
    if localdt == None:
        return localdt
    localtz = localdt.tzinfo
    if localtz is None:
        localtz = tz_utc()
        localdt = localdt.replace(tzinfo=localtz)
    if localtz == tz_utc():
        return localdt
    time_struct = time.mktime(localdt.timetuple())
    utcdt = datetime.datetime.utcfromtimestamp(time_struct)
    utcdt = utcdt.replace(tzinfo=tz_utc())
    return utcdt

def utc_to_local(utcdt, tz=None):
    """
        if tz is None, it is returned specificed datetime with localzone.
    """
    if utcdt is None:
        return utcdt
    tz = tz_timezone(tz)    
    if utcdt.tzinfo is None:
        utcdt = utcdt.replace(tzinfo=tz_utc())
    elif utcdt.tzinfo != tz_utc():
        raise ValueError("datetime is not in UTC timezone. - %s" % (utcdt.tzinfo))
    utcdt = utcdt.replace(tzinfo=tz_utc())
    localdt = utcdt.astimezone(tz)
    localdt = localdt.replace(tzinfo=None)
    return tz.localize(localdt)

def datetime_to_date(value):
    return datetime.date(value.year, value.month, value.day)

def date_to_datetime(value):
    return datetime.datetime(value.year, value.month, value.day, 0, 0, 0)

def format_datetime(value, fmt=None):
    s = datetime_to_str(value, fmt)
    return str_to_datetime(s, fmt)

def datetime_to_str(value, fmt=None):
    if fmt == None:
        if isinstance(value, datetime.datetime):
            fmt = datetime_format()
        else:
            fmt = date_format()
    return value.strftime(fmt)

def datetime_to_utc_timestamp(dt):
    """
    Converts a datetime instance to a timestamp.

    :type timeval: datetime
    :rtype: float
    """
    if dt is not None:
        return timegm(dt.utctimetuple()) + dt.microsecond / 1000000


def utc_timestamp_to_datetime(timestamp):
    """
    Converts the given timestamp to a datetime instance.
    :type timestamp: float
    :rtype: datetime
    """
    if timestamp is not None:
        return datetime.datetime.fromtimestamp(timestamp, tz_utc())


def timedelta_seconds(delta):
    """
    Converts the given timedelta to seconds.

    :type delta: timedelta
    :rtype: float
    """
    return delta.days * 24 * 60 * 60 + delta.seconds + \
        delta.microseconds / 1000000.0


def datetime_ceil(dateval):
    """
    Rounds the given datetime object upwards.

    :type dateval: datetime
    """
    if dateval.microsecond > 0:
        return dateval + timedelta(seconds=1, microseconds=-dateval.microsecond)
    return dateval

def time_seconds():
    return time.time()

def date_format():
    return "%Y-%m-%d"

def dateminute_format():
    return "%Y-%m-%d %H:%M"

def datesecond_format():
    return "%Y-%m-%d %H:%M:%S"

def datetime_format(regex=False):
    return "%Y-%m-%d %H:%M:%S.%f" if not regex else re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'(?: (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})'
    r'(?:\.(?P<microsecond>\d{1,6}))?)?')

class JsonMixin(object):
    """
        Object that is about to be JSON serialized should extend this object
    """
    def to_dict(self):
        raise NotImplementedError("JsonMixin.to_dict")

class ExtJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            df = '%Y-%m-%d %H:%M:%S'
            encoded_object = obj.strftime(df)
        elif isinstance(obj, datetime.date):
            df = '%Y-%m-%d'
            encoded_object = obj.strftime(df)
        elif isinstance(obj, JsonMixin):
            encoded_object = obj.to_dict()
        else:
            encoded_object = json.JSONEncoder.default(self, obj)
        return encoded_object

def obj_to_json(obj):
    return json.dumps(obj, ensure_ascii=False, cls=ExtJsonEncoder)

def json_to_object(jsonstr):
    if jsonstr is not None and jsonstr.strip() != '':
        return json.loads(jsonstr)
    else:
        return None

def list_group(seq, size): 
    """
    Returns an iterator over a series of lists of length size from iterable.

        >>> list(group([1,2,3,4], 2))
        [[1, 2], [3, 4]]
        >>> list(group([1,2,3,4,5], 2))
        [[1, 2], [3, 4], [5]]
    """
    def take(seq, n):
        for i in xrange(n):
            yield seq.next()

    if not hasattr(seq, 'next'):  
        seq = iter(seq)
    while True: 
        x = list(take(seq, size))
        if x:
            yield x
        else:
            break

def list_uniq(seq, key=None):
    """
    Removes duplicate elements from a list while preserving the order of the rest.

        >>> uniq([9,0,2,1,0])
        [9, 0, 2, 1]

    The value of the optional `key` parameter should be a function that
    takes a single argument and returns a key to test the uniqueness.

        >>> uniq(["Foo", "foo", "bar"], key=lambda s: s.lower())
        ['Foo', 'bar']
    """
    key = key or (lambda x: x)
    seen = set()
    result = []
    for v in seq:
        k = key(v)
        if k in seen:
            continue
        seen.add(k)
        result.append(v)
    return result

def list_restack(stack, index=0):
    """Returns the element at index after moving it to the top of stack.

           >>> x = [1, 2, 3, 4]
           >>> list_restack(x)
           1
           >>> x
           [2, 3, 4, 1]
    """
    x = stack.pop(index)
    stack.append(x)
    return x

def list_get(lst, ind, default=None):
    """
    Returns `lst[ind]` if it exists, `default` otherwise.
    
        >>> listget(['a'], 0)
        'a'
        >>> listget(['a'], 1)
        >>> listget(['a'], 1, 'b')
        'b'
    """
    if len(lst) - 1 < ind: 
        return default
    return lst[ind]

def queue_requeue(queue, index=-1):
    """Returns the element at index after moving it to the beginning of the queue.

        >>> x = [1, 2, 3, 4]
        >>> queue_requeue(x)
        4
        >>> x
        [4, 1, 2, 3]
    """
    x = queue.pop(index)
    queue.insert(0, x)
    return x

def dict_reverse(mapping):
    """
    Returns a new dictionary with keys and values swapped.
    
        >>> dictreverse({1: 2, 3: 4})
        {2: 1, 4: 3}
    """
    return dict([(value, key) for (key, value) in mapping.iteritems()])

def dict_find(dictionary, element):
    """
    Returns a key whose value in `dictionary` is `element` 
    or, if none exists, None.
    
        >>> d = {1:2, 3:4}
        >>> dictfind(d, 4)
        3
        >>> dictfind(d, 5)
    """
    for (key, value) in dictionary.iteritems():
        if element is value: 
            return key

def dict_findall(dictionary, element):
    """
    Returns the keys whose values in `dictionary` are `element`
    or, if none exists, [].
    
        >>> d = {1:4, 3:4}
        >>> dictfindall(d, 4)
        [1, 3]
        >>> dictfindall(d, 5)
        []
    """
    res = []
    for (key, value) in dictionary.iteritems():
        if element is value:
            res.append(key)
    return res

def dict_incr(dictionary, element):
    """
    Increments `element` in `dictionary`, 
    setting it to one if it doesn't exist.
    
        >>> d = {1:2, 3:4}
        >>> dictincr(d, 1)
        3
        >>> d[1]
        3
        >>> dictincr(d, 5)
        1
        >>> d[5]
        1
    """
    dictionary.setdefault(element, 0)
    dictionary[element] += 1
    return dictionary[element]

def dict_add(*dicts):
    """
    Returns a dictionary consisting of the keys in the argument dictionaries.
    If they share a key, the value from the last argument is used.
    
        >>> dictadd({1: 0, 2: 0}, {2: 1, 3: 1})
        {1: 0, 2: 1, 3: 1}
    """
    result = {}
    for dct in dicts:
        result.update(dct)
    return result

def dict_to_hash(dictionary):
    """
        http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
        works only for hashable items in dict
    """
    return hash(frozenset(dictionary.items()))

def to_uuid_hex_40():
    id1 = uuid.uuid1()
    md = md5()
    md.update(str(id1))
    hd = md.hexdigest()
    return hd

def to_uuid_hex_64():
    id1 = uuid.uuid1()
    sha = sha256()
    sha.update(str(id1))
    sha = sha.hexdigest()
    return sha

class Stack(object):
    
    def __init__(self, array):
        self._array = array
        
    def push(self, obj):
        self._array.append(obj)
    
    def peek(self):
        return self._array[len(self._array) - 1]
    
    def is_empty(self):
        return len(self._array) == 0
    
    def size(self):
        return len(self._array)
    
    def pop(self):
        return self._array.pop()

class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.    
    """
    def __getattr__(self, key): 
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __setattr__(self, key, value): 
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __repr__(self):     
        return '<Storage ' + dict.__repr__(self) + '>'

def storify(mapping, *requireds, **defaults):
    """
    Creates a `storage` object from dictionary `mapping`, raising `KeyError` if
    d doesn't have all of the keys in `requireds` and using the default 
    values for keys found in `defaults`.

    For example, `storify({'a':1, 'c':3}, b=2, c=0)` will return the equivalent of
    `storage({'a':1, 'b':2, 'c':3})`.
    
    If a `storify` value is a list (e.g. multiple values in a form submission), 
    `storify` returns the last element of the list, unless the key appears in 
    `defaults` as a list. Thus:
    
        >>> storify({'a':[1, 2]}).a
        2
        >>> storify({'a':[1, 2]}, a=[]).a
        [1, 2]
        >>> storify({'a':1}, a=[]).a
        [1]
        >>> storify({}, a=[]).a
        []
    
    Similarly, if the value has a `value` attribute, `storify will return _its_
    value, unless the key appears in `defaults` as a dictionary.
    
        >>> storify({'a':storage(value=1)}).a
        1
        >>> storify({'a':storage(value=1)}, a={}).a
        <Storage {'value': 1}>
        >>> storify({}, a={}).a
        {}
        
    Optionally, keyword parameter `_unicode` can be passed to convert all values to unicode.
    
        >>> storify({'x': 'a'}, _unicode=True)
        <Storage {'x': u'a'}>
        >>> storify({'x': storage(value='a')}, x={}, _unicode=True)
        <Storage {'x': <Storage {'value': 'a'}>}>
        >>> storify({'x': storage(value='a')}, _unicode=True)
        <Storage {'x': u'a'}>
    """
    _unicode = defaults.pop('_unicode', False)

    # if _unicode is callable object, use it convert a string to unicode.
    to_unicode = safeunicode
    if _unicode is not False and hasattr(_unicode, "__call__"):
        to_unicode = _unicode
    
    def unicodify(s):
        if _unicode and isinstance(s, str): return to_unicode(s)
        else: return s
        
    def getvalue(x):
        if hasattr(x, 'file') and hasattr(x, 'value'):
            return x.value
        elif hasattr(x, 'value'):
            return unicodify(x.value)
        else:
            return unicodify(x)
    
    stor = Storage()
    for key in requireds + tuple(mapping.keys()):
        value = mapping[key]
        if isinstance(value, list):
            if isinstance(defaults.get(key), list):
                value = [getvalue(x) for x in value]
            else:
                value = value[-1]
        if not isinstance(defaults.get(key), dict):
            value = getvalue(value)
        if isinstance(defaults.get(key), list) and not isinstance(value, list):
            value = [value]
        setattr(stor, key, value)

    for (key, value) in defaults.iteritems():
        result = value
        if hasattr(stor, key): 
            result = stor[key]
        if value == () and not isinstance(result, tuple): 
            result = (result,)
        setattr(stor, key, result)
    
    return stor

class IterBetter:
    """
    Returns an object that can be used as an iterator 
    but can also be used via __getitem__ (although it 
    cannot go backwards -- that is, you cannot request 
    `iterbetter[0]` after requesting `iterbetter[1]`).
    
        >>> import itertools
        >>> c = iterbetter(itertools.count())
        >>> c[1]
        1
        >>> c[5]
        5
        >>> c[3]
        Traceback (most recent call last):
            ...
        IndexError: already passed 3

    For boolean test, IterBetter peeps at first value in the itertor without effecting the iteration.

        >>> c = iterbetter(iter(range(5)))
        >>> bool(c)
        True
        >>> list(c)
        [0, 1, 2, 3, 4]
        >>> c = iterbetter(iter([]))
        >>> bool(c)
        False
        >>> list(c)
        []
    """
    def __init__(self, iterator): 
        self.i, self.c = iterator, 0

    def __iter__(self): 
        if hasattr(self, "_head"):
            yield self._head

        while 1:    
            yield self.i.next()
            self.c += 1

    def __getitem__(self, i):
        # todo: slices
        if i < self.c: 
            raise IndexError, "already passed " + str(i)
        try:
            while i > self.c: 
                self.i.next()
                self.c += 1
            # now self.c == i
            self.c += 1
            return self.i.next()
        except StopIteration: 
            raise IndexError, str(i)
            
    def __nonzero__(self):
        if hasattr(self, "__len__"):
            return len(self) != 0
        elif hasattr(self, "_head"):
            return True
        else:
            try:
                self._head = self.i.next()
            except StopIteration:
                return False
            else:
                return True

iters = [list, tuple]
if hasattr(__builtin__, 'set'):
    iters.append(set)
if hasattr(__builtin__, 'frozenset'):
    iters.append(set)
if sys.version_info < (2, 6):  # sets module deprecated in 2.6
    try:
        from sets import Set
        iters.append(Set)
    except ImportError: 
        pass
    
class _hack(tuple): pass
iters = _hack(iters)
iters.__doc__ = """
A list of iterable items (like lists, but not strings). Includes whichever
of lists, tuples, sets, and Sets are available in this version of Python.
"""

def safeunicode(obj, encoding='utf-8'):
    r"""
    Converts any given object to unicode string.
    
        >>> safeunicode('hello')
        u'hello'
        >>> safeunicode(2)
        u'2'
        >>> safeunicode('\xe1\x88\xb4')
        u'\u1234'
    """
    t = type(obj)
    if t is unicode:
        return obj
    elif t is str:
        return obj.decode(encoding)
    elif t in [int, float, bool]:
        return unicode(obj)
    elif hasattr(obj, '__unicode__') or isinstance(obj, unicode):
        return unicode(obj)
    else:
        return str(obj).decode(encoding)
    
def safestr(obj, encoding='utf-8'):
    r"""
    Converts any given object to utf-8 encoded string.     
        >>> safestr('hello')
        'hello'
        >>> safestr(u'\u1234')
        '\xe1\x88\xb4'
        >>> safestr(2)
        '2'
    """
    if isinstance(obj, unicode):
        return obj.encode(encoding)
    elif isinstance(obj, str):
        return obj
    elif hasattr(obj, 'next'):  # iterator
        return itertools.imap(safestr, obj)
    else:
        return str(obj)

def safeiter(it, cleanup=None, ignore_errors=True):
    """Makes an iterator safe by ignoring the exceptions occured during the iteration.
    """
    def next1():
        while True:
            try:
                return it.next()
            except StopIteration:
                raise
            except:
                traceback.print_exc()

    it = iter(it)
    while True:
        yield next1()


def utf8(string):
    """
    Make sure string is utf8 encoded bytes.

    If parameter is a object, object.__str__ will been called before encode as bytes
    """
    if isinstance(string, six.text_type):
        return string.encode('utf8')
    elif isinstance(string, six.binary_type):
        return string
    else:
        return six.text_type(string).encode('utf8')

def text(string, encoding='utf8'):
    """
    Make sure string is unicode type, decode with given encoding if it's not.

    If parameter is a object, object.__str__ will been called
    """
    if isinstance(string, six.text_type):
        return string
    elif isinstance(string, six.binary_type):
        return string.decode(encoding)
    else:
        return six.text_type(string)


def pretty_unicode(string):
    """
    Make sure string is unicode, try to decode with utf8, or unicode escaped string if failed.
    """
    if isinstance(string, six.text_type):
        return string
    try:
        return string.decode("utf8")
    except UnicodeDecodeError:
        return string.decode('Latin-1').encode('unicode_escape').decode("utf8")


def unicode_string(string):
    """
    Make sure string is unicode, try to default with utf8, or base64 if failed.

    can been decode by `decode_unicode_string`
    """
    if isinstance(string, six.text_type):
        return string
    try:
        return string.decode("utf8")
    except UnicodeDecodeError:
        return '[BASE64-DATA]' + base64.b64encode(string) + '[/BASE64-DATA]'


def unicode_dict(_dict):
    """
    Make sure keys and values of dict is unicode.
    """
    r = {}
    for k, v in iteritems(_dict):
        r[unicode_string(k)] = unicode_obj(v)
    return r


def unicode_list(_list):
    """
    Make sure every element in list is unicode. bytes will encode in base64
    """
    return [unicode_obj(x) for x in _list]


def unicode_obj(obj):
    """
    Make sure keys and values of dict/list/tuple is unicode. bytes will encode in base64.

    Can been decode by `decode_unicode_obj`
    """
    if isinstance(obj, dict):
        return unicode_dict(obj)
    elif isinstance(obj, (list, tuple)):
        return unicode_list(obj)
    elif isinstance(obj, six.string_types):
        return unicode_string(obj)
    elif isinstance(obj, (int, float)):
        return obj
    elif obj is None:
        return obj
    else:
        try:
            return text(obj)
        except:
            return text(repr(obj))

def decode_unicode_string(string):
    """
    Decode string encoded by `unicode_string`
    """
    if string.startswith('[BASE64-DATA]') and string.endswith('[/BASE64-DATA]'):
        return base64.b64decode(string[len('[BASE64-DATA]'):-len('[/BASE64-DATA]')])
    return string


def decode_unicode_obj(obj):
    """
    Decode unicoded dict/list/tuple encoded by `unicode_obj`
    """
    if isinstance(obj, dict):
        r = {}
        for k, v in iteritems(obj):
            r[decode_unicode_string(k)] = decode_unicode_obj(v)
        return r
    elif isinstance(obj, six.string_types):
        return decode_unicode_string(obj)
    elif isinstance(obj, (list, tuple)):
        return [decode_unicode_obj(x) for x in obj]
    else:
        return obj
    
def gen_empty_pager():
    pager = Storage()
    pager.total = 0
    pager.page = 1
    pager.count = 0
    pager.records = []
    return pager

def gen_pager(page, count, limit, records):
    total = int((count + limit - 1) / limit)
    pager = gen_empty_pager()
    pager.total = total
    if page > total:
        page = total
    pager.page = page
    pager.count = count
    pager.records = records
    return pager