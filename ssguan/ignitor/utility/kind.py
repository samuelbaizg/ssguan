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

"""
    builtin-types utility.
"""

from calendar import timegm
import calendar
import codecs
from datetime import tzinfo, timedelta
import datetime
from hashlib import md5, sha256
import json
import re
import time
import uuid

import pytz
from six import iteritems
import six
import tzlocal

import pickle as pickle
from ssguan.ignitor.base.struct import iters, ExtJsonEncoder, Memoize


if six.PY34 or six.PY2:
    RE_FLAG_UNICODE = re.UNICODE
    RE_FLAG_IGNORECASE = re.IGNORECASE  
    RE_FLAG_DOTALL = re.DOTALL
    RE_FLAG_DOTALL = re.UNICODE
else:
    RE_FLAG_UNICODE = re.RegexFlag.UNICODE
    RE_FLAG_IGNORECASE = re.RegexFlag.IGNORECASE
    RE_FLAG_DOTALL = re.RegexFlag.DOTALL
    RE_FLAG_DOTALL = re.RegexFlag.UNICODE
    
def is_str(value):
    """
        Check if value is string type or not
    """
    if six.PY2:
        if isinstance(value, (str, unicode)):
            return True
    else:
        if isinstance(value, (str)):
            return True
    return False

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
        raise ValueError("Direction needs to be r or l.")
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

def str_lower_first(value):
    """
        Convert the first alphabit to lowcase and keep the others unchange.
    """
    return value[0:1].lower() + value[1:]

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
    pickled = codecs.encode(pickle.dumps(value), "base64").decode()
    return pickled    

def pickle_to_obj(value):
    unpickled = pickle.loads(codecs.decode(value.encode(), "base64"))
    return unpickled

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
    except Exception as e:
        print(e)
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
        if isinstance(value, str):
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

def datetime_floor(dateval):
    """
    Rounds the given datetime object downwards.

    :type dateval: datetime
    """
    if dateval.microsecond > 0:
        return dateval + timedelta(seconds=0, microseconds=-dateval.microsecond)
    else:
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
        for i in range(n):
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

def generator_next(g):
    """
        Return next elements in generator.
        :param g|generator:
        :rtype generator: return None if stopping iteration.
    """
    try:
        e = g.__next__()
        return e
    except StopIteration:
        return None

def generator_concat(generators):
    """
        Concat multiple generators to one generator
    """
    for g in generators:
        for r in g:
            yield r


def generator_to_list(generator, max_count=None):
    """
        Convert generator to list
        :param max_count|int: the maximum element count to be joined.
    """
    datas = []
    count = 0
    for r in generator:
        count += 1
        datas.append(r)
        if max_count is not None and count >= max_count:
            break
    return datas

def generator_append(a, b):
    """
        Append b generator to a.
    """
    for r in a:
        yield r
    for r in b:
        yield r
        
def generator_merge(g1, g2):
    """
        Merge two generators.
        :param g1,g2|generator: the elements in generator must be the dict  
    """
    while True:
        d1 = generator_next(g1)
        if d1 is None:
            return
        d2 = generator_next(g2)
        if d2 is not None:
            for k in d2:
                d1[k] = d2[k]
        yield d1
        
def generator_cross(g1, g2):
    """
        Multiple all elements in generator g1 and all the elements in generator g2 .eg.
        g1 = [{'a':1,'b':2}, {'a':3,'b':4}],g2 = [{'c':1,'d':2}, {'c':3,'d':4}],return 
        [{'a':1,'b':2,'c':1,'d':2},{'a':1,'b':2,'c':3,'d':4},{'a':3,'b':4,'c':1,'d':2},{'a':3,'b':4,'c':3,'d':4}]
        :param g1,g2|generator: the elements in generator must be the dict.        
    """
    l = list(g2)
    for r1 in g1:
        r1 = dict.copy(r1)
        for r2 in l:
            for key in r2:
                r1[key] = r2[key]
            yield dict.copy(r1)

def generator_mix(g1, g2):
    """
        Mix the elements in generator g1,g2. Pick one from g1 then pick the other from g2.  
        :param g1,g2|generator: 
    """
    while True:
        r1 = generator_next(g1)
        if r1 is not None:
            yield r1
        r2 = generator_next(g2)
        if r2 is not None:
            yield r2
        if r1 is None and r2 is None:
            return

def dict_merge(d1, d2, keys=None):
    """
        Merge items of d2 to d1. if keys is None, merge all keys in d2.
        :param keys|str,list: the keys to be merged. 
    """
    if keys is None:
        for r in d2:
            d1[r] = d2[r]
    else:
        if type(keys) == str:
            keys = [keys]
        for r in keys:
            d1[r] = d2[r]
    return d1

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

def uuid_hex_32():
    id1 = uuid.uuid1()
    md = md5()
    md.update(unibytes(id1))
    hd = md.hexdigest()    
    return hd

def uuid_hex_64():
    id1 = uuid.uuid1()
    sha = sha256()
    sha.update(unibytes(id1))
    sha = sha.hexdigest()
    return sha

def safestr(obj, encoding='utf8'):
    """
    Make sure string is unicode type, decode with given encoding if it's not.

    If parameter is a object, object.__str__ will been called
    """
    if isinstance(obj, six.text_type):
        return obj
    elif isinstance(obj, six.binary_type):
        return obj.decode(encoding)
    else:
        return six.text_type(obj)

def safebinary(obj):
    """
    Make sure obj is binary type
    """
    if isinstance(obj, six.binary_type):
        return obj
    try:
        return six.binary_type(obj)
    except UnicodeEncodeError:
        return obj.encode('utf-8')
    
def unibytes(string):
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

def unidict(_dict):
    """
    Make sure keys and values of dict is unicode.
    """
    r = {}
    for k, v in iteritems(_dict):
        r[safestr(k)] = uniobject(v)
    return r


def unilist(_list):
    """
    Make sure every element in list is unicode. bytes will encode in base64
    """
    return [uniobject(x) for x in _list]


def uniobject(obj):
    """
    Make sure keys and values of dict/list/tuple is unicode. bytes will encode in base64.

    Can been decode by `decode_unicode_obj`
    """
    if isinstance(obj, dict):
        return unidict(obj)
    elif isinstance(obj, (list, tuple)):
        return unilist(obj)
    elif isinstance(obj, six.string_types):
        return safestr(obj)
    elif isinstance(obj, (int, float)):
        return obj
    elif obj is None:
        return obj
    else:
        try:
            return safestr(obj)
        except:
            return safestr(repr(obj))

def deuniobject(obj):
    """
    Decode unicoded dict/list/tuple encoded by `unicode_obj`
    """
    if isinstance(obj, dict):
        r = {}
        for k, v in iteritems(obj):
            r[safestr(k)] = deuniobject(v)
        return r
    elif isinstance(obj, six.string_types):
        return safestr(obj)
    elif isinstance(obj, (list, tuple)):
        return [deuniobject(x) for x in obj]
    else:
        return obj
        
re_compile = Memoize(re.compile)  # @@ threadsafe?
re_compile.__doc__ = """A memoized version of re.compile."""

def re_subm(pat, repl, string):
    """
    Like re.sub, but returns the replacement _and_ the match object.
    
        >>> t, m = re_subm('g(oo+)fball', r'f\\1lish', 'goooooofball')
        >>> t
        'foooooolish'
        >>> m.groups()
        ('oooooo',)
    """
    class re_subm_proxy:
        def __init__(self): 
            self.match = None
        def __call__(self, match): 
            self.match = match
            return ''
    compiled_pat = re_compile(pat)
    proxy = re_subm_proxy()
    compiled_pat.sub(proxy.__call__, string)
    return compiled_pat.sub(repl, string), proxy.match