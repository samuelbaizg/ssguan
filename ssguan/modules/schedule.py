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

from calendar import monthrange
from datetime import timedelta, datetime
import logging
import platform
import re
import sys

from tornado.ioloop import IOLoop, PeriodicCallback

from ssguan import config
from ssguan.commons import   dao, typeutils, funcutils
from ssguan.commons.dao import Model, UniqueValidator, ClassCastError
from ssguan.commons.error import Error, ExceptionWrap, NoFoundError
from ssguan.modules import auth
from ssguan.modules.auth import RoleOperation, UnauthorizedError


_logger = logging.getLogger(config.MODULE_SCHEDULE)

class CronExprError(Error):
    
    def __init__(self, field, expr):
        super(CronExprError, self).__init__('Unrecognized expression "{{expression}}" for field "{{propName}}"' , expression=expr, propName=field)
    
    @property
    def code(self):
        return 1140

class CJRunningError(Error):
    def __init__(self, job_id, job_name):
        super(CJRunningError, self).__init__("CronJob {{jobId}} {{jobName}} is running." , jobId=job_id, jobName=job_name)
        
    @property
    def code(self):
        return 1141

class SchedulerRunningError(Error):
    
    def __init__(self):
        super(SchedulerRunningError, self).__init__("Scheduler is already running.")
        
    @property
    def code(self):
        return 1132

class CJNotSavedError(Error):
    def __init__(self):
        super(CJNotSavedError, self).__init__("Cronjob is not saved.")
        
    @property
    def code(self):
        return 1133

class _FireExpr(object):
    
    WEEKDAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    value_re = re.compile(r'\*(?:/(?P<step>\d+))?$')

    def __init__(self, step=None):
        self.step = typeutils.str_to_int(step)
        if self.step == 0:
            raise ValueError('Increment must be higher than 0')

    def get_next_value(self, date, field):
        start = field.get_value(date)
        minval = field.get_min(date)
        maxval = field.get_max(date)
        start = max(start, minval)

        if not self.step:
            next1 = start
        else:
            distance_to_next = (self.step - (start - minval)) % self.step
            next1 = start + distance_to_next

        if next1 <= maxval:
            return next1

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.step == other.step

    def __str__(self):
        if self.step:
            return '*/%d' % self.step
        return '*'

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.step)


class _RangeFireExpr(_FireExpr):
    value_re = re.compile(
        r'(?P<first>\d+)(?:-(?P<last>\d+))?(?:/(?P<step>\d+))?$')

    def __init__(self, first, last=None, step=None):
        _FireExpr.__init__(self, step)
        first = typeutils.str_to_int(first)
        last = typeutils.str_to_int(last)
        if last is None and step is None:
            last = first
        if last is not None and first > last:
            raise ValueError('The minimum value in a range must not be higher than the maximum')
        self.first = first
        self.last = last

    def get_next_value(self, date, field):
        startval = field.get_value(date)
        minval = field.get_min(date)
        maxval = field.get_max(date)

        # Apply range limits
        minval = max(minval, self.first)
        maxval = min(maxval, self.last) if self.last is not None else maxval
        nextval = max(minval, startval)

        # Apply the step if defined
        if self.step:
            distance_to_next = (self.step - (nextval - minval)) % self.step
            nextval += distance_to_next

        return nextval if nextval <= maxval else None

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.first == other.first and
                self.last == other.last)

    def __str__(self):
        if self.last != self.first and self.last is not None:
            range1 = '%d-%d' % (self.first, self.last)
        else:
            range1 = str(self.first)

        if self.step:
            return '%s/%d' % (range1, self.step)
        return range1

    def __repr__(self):
        args = [str(self.first)]
        if self.last != self.first and self.last is not None or self.step:
            args.append(str(self.last))
        if self.step:
            args.append(str(self.step))
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


class _WeekdayRangeFireExpr(_RangeFireExpr):
    value_re = re.compile(r'(?P<first>[a-z]+)(?:-(?P<last>[a-z]+))?', re.IGNORECASE)

    def __init__(self, first, last=None):
        try:
            first_num = self.WEEKDAYS.index(first.lower())
        except ValueError:
            raise ValueError('Invalid weekday name "%s"' % first)

        if last:
            try:
                last_num = self.WEEKDAYS.index(last.lower())
            except ValueError:
                raise ValueError('Invalid weekday name "%s"' % last)
        else:
            last_num = None

        _RangeFireExpr.__init__(self, first_num, last_num)

    def __str__(self):
        if self.last != self.first and self.last is not None:
            return '%s-%s' % (self.WEEKDAYS[self.first], self.WEEKDAYS[self.last])
        return self.WEEKDAYS[self.first]

    def __repr__(self):
        args = ["'%s'" % self.WEEKDAYS[self.first]]
        if self.last != self.first and self.last is not None:
            args.append("'%s'" % self.WEEKDAYS[self.last])
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


class _WeekdayPositionFireExpr(_FireExpr):
    options = ['1st', '2nd', '3rd', '4th', '5th', 'last']
    value_re = re.compile(r'(?P<option_name>%s) +(?P<weekday_name>(?:\d+|\w+))' % 
                          '|'.join(options), re.IGNORECASE)

    def __init__(self, option_name, weekday_name):
        try:
            self.option_num = self.options.index(option_name.lower())
        except ValueError:
            raise ValueError('Invalid weekday position "%s"' % option_name)

        try:
            self.weekday = self.WEEKDAYS.index(weekday_name.lower())
        except ValueError:
            raise ValueError('Invalid weekday name "%s"' % weekday_name)

    def get_next_value(self, date, field):
        # Figure out the weekday of the month's first day and the number of days in that month
        first_day_wday, last_day = monthrange(date.year, date.month)

        # Calculate which day of the month is the first of the target weekdays
        first_hit_day = self.weekday - first_day_wday + 1
        if first_hit_day <= 0:
            first_hit_day += 7

        # Calculate what day of the month the target weekday would be
        if self.option_num < 5:
            target_day = first_hit_day + self.option_num * 7
        else:
            target_day = first_hit_day + ((last_day - first_hit_day) // 7) * 7

        if target_day <= last_day and target_day >= date.day:
            return target_day

    def __eq__(self, other):
        return (super(_WeekdayPositionFireExpr, self).__eq__(other) and
                self.option_num == other.option_num and self.weekday == other.weekday)

    def __str__(self):
        return '%s %s' % (self.options[self.option_num], self.WEEKDAYS[self.weekday])

    def __repr__(self):
        return "%s('%s', '%s')" % (self.__class__.__name__, self.options[self.option_num],
                                   self.WEEKDAYS[self.weekday])


class _LastDayOfMonthFireExpr(_FireExpr):
    value_re = re.compile(r'last', re.IGNORECASE)

    def __init__(self):
        pass

    def get_next_value(self, date, field):
        return monthrange(date.year, date.month)[1]

    def __str__(self):
        return 'last'

    def __repr__(self):
        return "%s()" % self.__class__.__name__

class _FireProperty(dao.StringProperty):
    
    COMPILERS = [_FireExpr, _RangeFireExpr]
    
    def __init__(self, label, minimum, maximum, default):        
        super(_FireProperty, self).__init__(label, default=default, length=10, required=True, validator=None, choices=None, logged=True)
        self._minimum = minimum
        self._maximum = maximum
    
    def is_real(self):
        return True
    
    def get_min(self, dateval):
        return self._minimum

    def get_max(self, dateval):
        return self._maximum

    def get_value(self, dateval):
        name = self.aware_name
        return getattr(dateval, name)
    
    @property
    def aware_name(self):
        name = self.name[5:] if self.name.startswith("fire_") else self.name
        return name

    def get_next_value(self, exprs, dateval):
        smallest = None
        expressions = self.compile_expressions(exprs)
        for expr in expressions:
            value = expr.get_next_value(dateval, self)
            if smallest is None or (value is not None and value < smallest):
                smallest = value
        return smallest
    
    def compile_expressions(self, exprs):
        expressions = []
        # Split a comma-separated expression list, if any
        exprs = str(exprs).strip()
        if ',' in exprs:
            for expr in exprs.split(','):
                expr = str(expr).strip()
                expressions.append(self.compile_expression(expr))
        else:
            expressions.append(self.compile_expression(exprs))
        return expressions
        
    def compile_expression(self, expr):
        for compiler in self.COMPILERS:
            match = compiler.value_re.match(expr)
            if match:
                compiled_expr = compiler(**match.groupdict())
                return compiled_expr                
        raise CronExprError(self.get_label(), self.value)
    
    @property
    def is_default(self):
        return self.value == self.default_value()
    
    def __set__(self, model_instance, value):
        dao.StringProperty.__set__(self, model_instance, value)
        self.value = value
        
    def __eq__(self, other):
        return isinstance(self, self.__class__) and self.value == other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "%s('%s', '%s')" % (self.__class__.__name__, self.name, self)
        
class _WeekProperty(_FireProperty):
    def is_real(self):
        return False

    def get_value(self, dateval):
        return dateval.isocalendar()[1]


class _DayOfMonthProperty(_FireProperty):
    COMPILERS = _FireProperty.COMPILERS + [_WeekdayPositionFireExpr, _LastDayOfMonthFireExpr]

    def get_max(self, dateval):
        return monthrange(dateval.year, dateval.month)[1]


class _DayOfWeekProperty(_FireProperty):
    COMPILERS = _FireProperty.COMPILERS + [_WeekdayRangeFireExpr]

    def is_real(self):
        return False
    
    def get_value(self, dateval):
        return dateval.weekday()
    
class CJRunner(object):
    
    def __init__(self, cronjob):
        self._cronjob = cronjob
    
    @property
    def cronjob(self):
        return self._cronjob
    
    def run(self, cjrunlog, caller):
        raise NotImplementedError("CJRunner.run")
    
    def run_success_cb(self, result, cjrunlog, caller):
        """Do nothing. Override by sub-class for specific need."""
        
    def run_failure_cb(self, exception, cjrunlog, caller):
        """Do nothing. Override by sub-class for specific need."""

    
class CronJob(Model):
    
    """
    :param int|str year: 4-digit year
    :param int|str month: month (1-12)
    :param int|str day: day of the (1-31)
    :param int|str week: ISO week (1-53)
    :param int|str day_of_week: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    :param int|str hour: hour (0-23)
    :param int|str minute: minute (0-59)
    :param int|str second: second (0-59)
    :param datetime start_date: earliest possible datetime to trigger on (inclusive)
    :param datetime end_date: latest possible datetime to trigger on (inclusive)
    :param str timezone: time zone to use for the datetime calculations (defaults
        to UTC)
    :ivar int run_status: current running status of job (``RUN_STATUS_SUCCESS``, ``RUN_STATUS_RUNNING``, ``RUN_STATUS_FAILED``)

    .. note:: The first weekday is always **monday**.
    """
    RUN_STATUS_SUCCESS = 0
    RUN_STATUS_RUNNING = 1
    RUN_STATUS_FAILED = 2
    
    
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_SCHEDULE
    
    job_name = dao.StringProperty("jobName", required=True, validator=UniqueValidator("job_name"), logged=True)
    job_group = dao.StringProperty("jobGroup", required=False, logged=True)    
    job_desc = dao.StringProperty("jobDesc", length=2000, required=False, logged=True)
    job_runner = dao.StringProperty("jobRunner", length=500, required=True, validator=None, choices=None, logged=True)
    job_node = dao.StringProperty("jobNode", required=True, logged=True)
    run_params = dao.DictProperty("runParams", required=False, length=65535, logged=True)    
    broken = dao.BooleanProperty("broken", required=True, default=False, logged=True)
    singleton = dao.BooleanProperty("singleton", required=True, default=True, logged=True)
    logged = dao.BooleanProperty("logged", required=True, default=True, logged=True)
    fire_year = _FireProperty("fireYear", 1970, 2 ** 63, '*')
    fire_month = _FireProperty("fireMonth", 1, 12, 1)
    fire_day = _FireProperty("fireDay", 1, 31, 1)
    fire_week = _WeekProperty("fireWeek", 1, 53, '*')
    fire_dayofweek = _DayOfWeekProperty("fireDayofweek", 0, 6, '*')
    fire_hour = _FireProperty("fireHour", 0, 23, 0)
    fire_minute = _FireProperty("fireMinute", 0, 59, 0)
    fire_second = _FireProperty("fireSecond", 0, 59, 0)
    start_time = dao.DateTimeProperty("startTime", required=False, logged=True)
    end_time = dao.DateTimeProperty("endTime", required=False, logged=True)
    timezone = dao.TimezoneProperty("timezone", default=typeutils.tz_utc(), logged=True)
    previous_run_time = dao.DateTimeProperty("previousRunTime", required=False)
    next_run_time = dao.DateTimeProperty("nextRunTime", required=False)

    def __init__(self, entityinst=False, **kwds):
        super(CronJob, self).__init__(entityinst=entityinst, **kwds)
        self._run_lock = funcutils.create_lock(False)
    
    @classmethod
    def get_by_name(cls, job_name):
        query = CronJob.all()
        query.filter("job_name =", job_name)
        return query.get()
    
    def get_fire_props(self):
        fire_props = []
        fire_props.append(self.get_property("fire_year"))
        fire_props.append(self.get_property("fire_month"))
        fire_props.append(self.get_property("fire_day"))
        fire_props.append(self.get_property("fire_week"))
        fire_props.append(self.get_property("fire_dayofweek"))
        fire_props.append(self.get_property("fire_hour"))
        fire_props.append(self.get_property("fire_minute"))
        fire_props.append(self.get_property("fire_second"))
        return fire_props
    
    def get_fire_period(self):
        """
            Return earliest and latest possible date/time to trigger on (inclusive)
            :rtype: tuple(start_time, end_time, timezone)
        """
        if self.timezone:
            timezone = typeutils.tz_timezone(self.timezone)    
        elif self.start_time and self.start_time.tzinfo:
            timezone = self.start_time.tzinfo
        elif self.end_time and self.end_time.tzinfo:
            timezone = self.end_time.tzinfo
        else:
            timezone = typeutils.tz_utc()
        if self.start_time is not None:
            start_time = self.start_time.replace(tzinfo=None)
            start_time = timezone.localize(start_time)
        else:
            start_time = None
        if self.end_time is not None:
            end_time = self.end_time.replace(tzinfo=None)
            end_time = timezone.localize(end_time)
        else:
            end_time = None 
        
        return (start_time, end_time, timezone)
       
    
    def get_next_fire_time(self, previous_run_time, now):
        if self.broken:
            return None
        fire_props = self.get_fire_props()
        (job_start_time, job_end_time, job_timezone) = self.get_fire_period()
        if previous_run_time:
            if previous_run_time.tzinfo == typeutils.tz_utc():            
                previous_run_time = typeutils.utc_to_local(previous_run_time, tz=job_timezone)
            else:
                if previous_run_time.tzinfo != job_timezone:
                    previous_run_time = typeutils.local_to_utc(previous_run_time)
                    previous_run_time = typeutils.utc_to_local(previous_run_time, tz=job_timezone)
            start_time = min(now, previous_run_time + timedelta(microseconds=1))
            if start_time == previous_run_time:
                start_time += timedelta(microseconds=1)
        else:
            start_time = max(now, job_start_time) if job_start_time else now
        fieldnum = 0
        next_time = typeutils.datetime_ceil(start_time)
        while 0 <= fieldnum < len(fire_props):
            field = fire_props[fieldnum]            
            curr_value = field.get_value(next_time)
            exprs = getattr(self, field.name)
            next_value = field.get_next_value(exprs, next_time)

            if next_value is None:
                # No valid value was found
                next_time, fieldnum = self._increment_field_value(next_time, fieldnum - 1, fire_props, job_timezone)
            elif next_value > curr_value:
                # A valid, but higher than the starting value, was found
                if field.is_real():
                    next_time = self._set_field_value(next_time, fieldnum, next_value, fire_props, job_timezone)
                    fieldnum += 1
                else:
                    next_time, fieldnum = self._increment_field_value(next_time, fieldnum, fire_props, job_timezone)
            else:
                # A valid value was found, no changes necessary
                fieldnum += 1
            if next_time is None:
                return None
            # Return if the date has rolled past the end date
            if job_end_time and next_time > job_end_time:
                return None

        if fieldnum >= 0:
            return typeutils.local_to_utc(next_time)
        else:
            return None
    
    def _before_create(self, key=None, dbconn=None):
        self.next_run_time = self.get_next_fire_time(None, typeutils.utcnow())
        
    def _after_create(self, key=None, dbconn=None):
        self._job_runner_inst = self._get_job_runner_inst()
        self._run_lock = funcutils.create_lock(False)
    
    def _before_update(self, dbconn=None):
        self.next_run_time = self.get_next_fire_time(self.previous_run_time, typeutils.utcnow())
    
    def _after_update(self, dbconn=None):
        self._job_runner_inst = self._get_job_runner_inst()
    
    def is_running(self):
        query = CJRunLog.all()
        query.filter("job_id =", self.key())
        query.filter("run_status =", CronJob.RUN_STATUS_RUNNING)
        return query.count() > 0
    
    def run_once(self, caller):
        if self.key() is None:
            raise CJNotSavedError()
        job_executor = funcutils.funcexector(1, process=False)
        job_executor.start()
        job_executor.submit(self._run_once_real, self._run_once_success, self._run_once_failure, caller)        
        job_executor.shutdown(wait=True)
    
    def _run_once_real(self, caller):        
        cjrunlog = None
        try:
            if self.singleton and self.is_running() :
                cjrunlog = self._start_once(caller)
                raise CJRunningError(self.key(), self.job_name)
            cjrunlog = self._start_once(caller)
            run_result = self._job_runner_inst.run(cjrunlog, caller)
            return (run_result, cjrunlog, caller)
        except:
            raise ExceptionWrap(sys.exc_info(), cjrunlog=cjrunlog, caller=caller)            
    
    def _run_once_success(self, result):
        (run_result, cjrunlog, caller) = (result[0], result[1], result[2])
        try:
            run_result = self._job_runner_inst.run_success_cb(run_result, cjrunlog, caller)        
        except Exception, e:
            _logger.error(e.message, exc_info=1)
        finally:
            try:
                self._complete_once(cjrunlog, CronJob.RUN_STATUS_SUCCESS, run_result, caller)
            except Exception, e:
                _logger.error(e.message, exc_info=1)
            
    def _run_once_failure(self, exc_info):
        exc = exc_info[1]
        cjrunlog = exc.data['cjrunlog']
        caller = exc.data['caller']
        try:
            _logger.error("failed to run cronjob\n%s\n%s", str(exc.exception), exc.message_tb)
            self._job_runner_inst.run_failure_cb(exc.exception, cjrunlog, caller)
        except Exception , e:
            _logger.error(e.message, exc_info=1)
        finally:
            try:
                self._complete_once(cjrunlog, CronJob.RUN_STATUS_FAILED, str(exc.exception), caller)
            except Exception, e:
                _logger.error(e.message, exc_info=1)
    
    def _increment_field_value(self, dateval, fieldnum, fire_props, timezone):
        """
        Increments the designated field and resets all less significant fields to their minimum
        values.

        :type dateval: datetime
        :type fieldnum: int
        :return: a tuple containing the new date, and the number of the field that was actually
            incremented
        :rtype: tuple
        """
        values = {}
        i = 0
        while i < len(fire_props):
            field = fire_props[i]
            if not field.is_real():
                if i == fieldnum:
                    fieldnum -= 1
                    i -= 1
                else:
                    i += 1
                continue

            if i < fieldnum:
                values[field.aware_name] = field.get_value(dateval)
                i += 1
            elif i > fieldnum:
                values[field.aware_name] = field.get_min(dateval)
                i += 1
            else:
                value = field.get_value(dateval)
                maxval = field.get_max(dateval)
                if value == maxval:
                    fieldnum -= 1
                    i -= 1
                else:
                    values[field.aware_name] = value + 1
                    i += 1
        
        lastday = monthrange(values['year'], values['month'])[1]
        if lastday < values['day']:
            return None, fieldnum
        else:
            difference = datetime(**values) - dateval.replace(tzinfo=None)
            return timezone.normalize(dateval + difference), fieldnum
        
        

    def _set_field_value(self, dateval, fieldnum, new_value, fire_props, timezone):
        values = {}
        for i, field in enumerate(fire_props):
            if field.is_real():
                if i < fieldnum:
                    values[field.aware_name] = field.get_value(dateval)
                elif i > fieldnum:
                    values[field.aware_name] = field.get_min(dateval)
                else:
                    values[field.aware_name] = new_value

        return timezone.localize(datetime(**values))
    
    def _start_once(self, caller):
        self._run_lock.acquire()
        dbconn = None
        cjrunlog = None   
        now = typeutils.utcnow()     
        if self.logged:
            cjrunlog = CJRunLog()
            cjrunlog.job_id = self.key()
            cjrunlog.job_name = self.job_name
            cjrunlog.run_status = CronJob.RUN_STATUS_RUNNING
            cjrunlog.run_progress = []
            cjrunlog.start_time = now
            cjrunlog = cjrunlog.create(caller, dbconn=dbconn)            
        try:
            self.next_run_time = self.get_next_fire_time(self.previous_run_time, now)
            self.previous_run_time = now                    
            self.update(caller)
        except Exception, e:
            if self.logged:
                cjrunlog.delete(caller, dbconn=dbconn)
            raise e
        self._run_lock.release()
        return cjrunlog
    
    def _complete_once(self, cjrunlog, run_status, run_result, caller, dbconn=None):
        if cjrunlog is not None:        
            self._run_lock.acquire()
            cjrunlog.run_status = run_status
            cjrunlog.run_result = str(run_result)
            cjrunlog.end_time = typeutils.utcnow()
            cjrunlog = cjrunlog.update(caller, dbconn=dbconn)        
            self._run_lock.release()
        return cjrunlog
    
    def _get_job_runner_inst(self):
        job_runner_clazz = funcutils.import_module(self.job_runner)
        if job_runner_clazz is None:
            raise NoFoundError("JobRunner", self.job_runner)
        if not issubclass(job_runner_clazz, CJRunner):
            raise ClassCastError(job_runner_clazz, CJRunner)
        return job_runner_clazz(self)
    
class CJRunLog(Model):
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_SCHEDULE
    job_id = dao.StringProperty("jobId", required=True)
    job_name = dao.StringProperty("jobName", required=True)
    start_time = dao.DateTimeProperty("startTime", required=True)
    end_time = dao.DateTimeProperty("endTime", required=False)    
    run_status = dao.IntegerProperty("runStatus", required=True, choices=[CronJob.RUN_STATUS_SUCCESS, CronJob.RUN_STATUS_RUNNING, CronJob.RUN_STATUS_FAILED])
    # [(25.0, "progress memo 1",'yyyy-MM-dd HH:mm:ss'),(30.0, "progress memo 2",'yyyy-MM-dd HH:mm:ss')]
    run_progress = dao.ListProperty("runProgress", required=True)
    run_result = dao.StringProperty("runResult", required=False)
    
    def update_progress(self, run_progress, progress_desc, caller):
        """
            update running progress of job
            :param run_progress|float: the percentage of running progress
            :param progress_momo|str: the progress memo
        """
        if self.run_progress is None:
            self.run_progress = []
        self.run_progress.append((run_progress, progress_desc, typeutils.utcnow()))
        self.run_status = CronJob.RUN_STATUS_RUNNING
        self.update(caller)

class Scheduler(object):
    
    _lock = funcutils.create_rlock(process=False)
    
    def __new__(cls, node):  
        with cls._lock:
            if not hasattr(cls, '_instances'):
                cls._instances = {}
            if not cls._instances.has_key(node):
                orig = super(Scheduler, cls) 
                instance = orig.__new__(cls)
                instance._node = node
                instance._periodic_callback = None
                cls._instances[node] = instance  
        return cls._instances[node]
    
    def start(self, interval, io_loop=None):
        if self.is_running():
            raise SchedulerRunningError()
        func = funcutils.wrap_func(self.run_once, Model.NULL_USER_ID)
        self._periodic_callback = PeriodicCallback(func, interval * 1000)                
        self._periodic_callback.start()
        if io_loop is None:
            io_loop = IOLoop.current()
        _logger.info("Scheduler %s is running per %d seconds." % (self._node, interval))
        io_loop.start()
    
    def stop(self):
        if self.is_running():
            self._periodic_callback.stop()
            self._periodic_callback = None
        else:
            self._periodic_callback = None
            
    def is_running(self):
        state = False
        if self._periodic_callback is None:
            state = False
        else:
            state = self._periodic_callback.is_running()
        return state
    
    def run_all(self, caller, broken=None):
        query = CronJob.all()    
        query.filter("job_node =", self._node)        
        query.filter("next_run_time <=", typeutils.utcnow())
        if broken is not None:
            query.filter("broken =", broken)
        cronjobs = query.fetch()
        for cronjob in cronjobs:
            cronjob.run_once(caller)
    
    def run_once(self, job_id, caller):
        cronjob = CronJob.get_by_key(job_id)
        cronjob.run_once(caller)

def create_cronjob(job_name, job_desc, job_runner, job_node, created_by, job_group=None, run_params=None, broken=False, logged=True, singleton=True, fire_year='*', fire_month=1, fire_day=1, fire_week='*', fire_dayofweek='*', fire_hour=0, fire_minute=0, fire_second=0, start_time=None, end_time=None, timezone=typeutils.tz_utc()):
    if not auth.has_permission(created_by, CronJob, RoleOperation.OPERATION_CREATE):
        raise UnauthorizedError(RoleOperation.OPERATION_CREATE, CronJob.get_modelname(), job_name)
    cronjob = CronJob(job_name=job_name, job_runner=job_runner)
    cronjob.job_desc = job_desc
    cronjob.job_node = job_node
    cronjob.job_group = job_group
    cronjob.run_params = run_params
    cronjob.broken = broken
    cronjob.singleton = singleton
    cronjob.logged = logged
    cronjob.fire_year = fire_year
    cronjob.fire_month = fire_month
    cronjob.fire_day = fire_day
    cronjob.fire_week = fire_week
    cronjob.fire_dayofweek = fire_dayofweek
    cronjob.fire_hour = fire_hour
    cronjob.fire_minute = fire_minute
    cronjob.fire_second = fire_second
    cronjob.start_time = start_time
    cronjob.end_time = end_time
    cronjob.timezone = timezone
    cronjob.previous_run_time = None
    if not broken:
        cronjob.next_run_time = cronjob.get_next_fire_time(None, typeutils.utcnow())
    else:
        cronjob.next_run_time = None
    cronjob.create(created_by)
    return cronjob

def get_cronjob(read_by, job_id=None, job_name=None):
    if not auth.has_permission(read_by, CronJob, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, CronJob.get_modelname(), "%s%s" % (job_id, job_name))
    cronjob = None
    if job_id is not None:
        cronjob = CronJob.get_by_key(job_id)            
    if cronjob is None and job_name is not None:
        cronjob = CronJob.get_by_name(job_name)
    return cronjob
    
def break_cronjob(job_id, broken, modified_by):
    if not auth.has_permission(modified_by, CronJob, RoleOperation.OPERATION_UPDATE):
        raise UnauthorizedError(RoleOperation.OPERATION_UPDATE, CronJob.get_modelname(), job_id)
    cronjob = CronJob.get_by_key(job_id)
    cronjob.broken = broken
    cronjob = cronjob.update(modified_by)
    return cronjob
    
def delete_cronjob(job_id, deleted_by):
    if not auth.has_permission(deleted_by, CronJob, RoleOperation.OPERATION_DELETE):
        raise UnauthorizedError(RoleOperation.OPERATION_DELETE, CronJob.get_modelname(), job_id)
    cronjob = CronJob.get_by_key(job_id)
    return cronjob.delete(deleted_by)

def fetch_cronjobs(read_by, job_name=None, job_node=None, job_group=None, broken=None):
    if not auth.has_permission(read_by, CronJob, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, CronJob.get_modelname(), "%s,%s,%s,%s" % (job_name, job_node, job_group, str(broken)))
    query = CronJob.all()
    if job_name is not None:
        query.filter("job_name like", '%%%s%%' % job_name)
    if job_node is not None:
        query.filter("job_node =", job_node)
    if job_group is not None:
        query.filter("job_group =", job_group)
    if broken is not None:
        query.filter("broken =", broken)
    return query.fetch()

def start(node, interval=1, io_loop=None):
    node = platform.node() if node is None else node
    scheduler = Scheduler(node)
    scheduler.start(interval, io_loop=io_loop)



def install_module():
    CronJob.create_schema()
    CJRunLog.create_schema()
    config.dbCFG.add_model_dbkey("%s_*" % config.MODULE_SCHEDULE, config.dbCFG.ROOT_DBKEY)
    return True

def uninstall_module():
    CronJob.delete_schema()
    CJRunLog.delete_schema()
    config.dbCFG.delete_model_dbkey("%s_*" % config.MODULE_SCHEDULE)
    return True
