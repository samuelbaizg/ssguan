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
import calendar
import pytz

def daysofmonth(year, month):
        return calendar.monthrange(year, month)[1]
    
def utcnow():
    return datetime.datetime.utcnow()

def utctoday():
    now = utcnow()
    return datetime.date(now.year, now.month, now.day)

def localnow(tzstr):
    now = utcnow()
    local = to_local(now, tzstr)
    return to_local(local, tzstr)

def localtoday(tzstr):
    now = utcnow()
    local = to_local(now, tzstr)
    return to_date(local)

def to_utc(dt, tzstr=pytz.utc):
    if dt != None:
        tzstr = str(tzstr)
        tz = pytz.timezone(tzstr)
        dt = dt.replace(tzinfo=tz)
        dt = dt.astimezone(pytz.utc) 
        if tzstr == "Asia/Shanghai":
            dt += datetime.timedelta(minutes=6)
    return dt

def to_local(utcdt, tzstr):
    if utcdt != None:
        tzstr = str(tzstr)
        tz = pytz.timezone(tzstr)
        utcdt = utcdt.replace(tzinfo=tz)
        utcdt = utcdt.astimezone(tz)
        if tzstr == "Asia/Shanghai":
            utcdt += datetime.timedelta(hours=8)
    return utcdt

def get_utczone():
    return pytz.utc

def to_date(value):
    return datetime.date(value.year, value.month, value.day)

def to_unaware(dt, tzstr=pytz.UTC):
    dt = to_utc(dt, tzstr)
    dt.replace(tzinfo=pytz.UTC)
    return dt
