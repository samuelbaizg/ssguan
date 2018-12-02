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

import imp
import os
import time

import six

from ssguan.ignitor import IGNITOR_DOMAIN
from ssguan.ignitor.asyn import logger
from ssguan.ignitor.asyn.conduit import Conduit
from ssguan.ignitor.orm import properti
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.utility import kind, parallel
from ssguan.ignitor.base.error import NoFoundError


class DBConduit(Conduit):
    
    CK_MAX_ATTEMPTS = "max_attempts"
    CK_PULL_TIMESPAN = "timespan"  # seconds
    
    def __init__(self, conduit_name, **kwargs):
        super(DBConduit, self).__init__(conduit_name, **kwargs)
        self.__msgclazz = self.__build_msg_clazz(conduit_name)
        self.__max_attempts = kwargs[self.CK_MAX_ATTEMPTS] if self.CK_MAX_ATTEMPTS in  kwargs else 3
        self.__timespan = kwargs[self.CK_PULL_TIMESPAN] if self.CK_PULL_TIMESPAN in  kwargs else 1
        self.__stopped = True
        self.__lock = parallel.create_lock(False)
        
    def send(self, message):
        msgmodel = self.__msgclazz()
        msgmodel.payload = message
        msgmodel.last_consumed_by = None
        msgmodel.last_consume_time = None
        msgmodel.last_error = None
        msgmodel = msgmodel.create(None)
        return True
    
    def process_success(self, message):
        try:
            msgmodel = self.__msgclazz.get_by_key(message.id)
            msgmodel.complete()
        except Exception as e:           
            msgid = message.id if message is not None else None
            logger.error("failed to execute callback when message %s is processed successfully: %s" % (msgid, str(e)), exc_info=1)
        
    def process_fail(self, error, message):
        try:
            msgmodel = self.__msgclazz.get_by_key(message.id)        
            msgmodel.error(error)
        except BaseException as e:
            msgid = message.id if message is not None else None
            logger.error("failed to execute failed callback when message %s is processed in failure." % msgid + str(e), exc_info=1)
    
    def start(self):       
        try:
            self.__lock.acquire()
            if self.__stopped:
                self.__stopped = False
                if not self.__msgclazz.has_schema():
                    self.__msgclazz.create_schema()
                job_executor = parallel.funcexector(1, process=False)
                job_executor.start()
                job_executor.submit(self.__start_real, self.__start_success, self.__start_fail)        
                job_executor.shutdown(wait=False)
            else:
                logger.warning("this conduit %s was already started." % self.name)
        finally:
            self.__lock.release()
    
    def __start_real(self):
        while(not self.__stopped):
            message = self.next_message()
            try:
                if message is not None:
                    self.consume(message)
                time.sleep(self.__timespan)
            except:
                logger.error("pull message error", exc_info=1)
        return True
    
    def __start_success(self, result):
        logger.info("succeed to start DBConsuit %s %s" % (self.name, result))
        
    
    def __start_fail(self, exc_info):       
        exc = exc_info[1]
        logger.error("failed to init DBConsuit %s %s." % (self.name , str(exc)), exc_info=1)
        
    def stop(self):        
        self.__stopped = True
        logger.info("succeed to stop DBConsuit %s." % (self.name))
    
    def next_message(self):       
        query = self.__msgclazz.all()
        query.filter("pull_flag =", False)
        query.filter("pull_time is", None)
        query.filter("attempts <= ", self.__max_attempts)
        query.set("pull_flag", True)   
        query.set("pull_time", kind.utcnow())
        query.set("consume_time", None)
        query.set("consume_error", None)
        msgmodel = query.find_one_and_update(None, new=True)       
        if msgmodel is not None: 
            message = msgmodel.payload
            message.id = (msgmodel.key())
        else:
            message = None
        return message
    
    def get_message(self, id1):
        """
            get message by message id
            :param id1|str: the id of message
        """
        msgmodel = self.__msgclazz.get_by_key(id1)
        if msgmodel is not None:
            message = msgmodel.payload
            message.id = (msgmodel.key())
        else:
            message = None
        return message
    
    def retry(self, id1):
        """
            put back the message to the conduit
            :param id1|str: the id of message
        """
        msgmodel = self.__msgclazz.get_by_key(id1)
        if msgmodel is not None:
            msgmodel.retry()
            return True
        else:
            raise NoFoundError("message", id1)
        
    
    def clear(self):
        """
            clear the conduit            
        """
        query = self.__msgclazz.all()
        return query.delete(None)
    
    def size(self):
        """
            return the message count of the conduit
        """
        query = self.__msgclazz.all()
        return query.count()
    
    def __build_msg_clazz(self, qname):
        clazzcode = """
from ssguan.ignitor.asyn.dbconduit import __MessageModel
class %s (__MessageModel):
    ''''''
        """ % (qname)
        clazz = compile(clazzcode, '<%s>' % qname, 'exec')
        mod = imp.new_module('ssguan.ignitor.asyn.conduit')
        mod.__file__ = '<%s>' % os.path.join(os.path.dirname(__file__) , 'asyn')
        mod.__loader__ = __name__
        mod.__package__ = 'ssguan.ignitor.asyn'
        six.exec_(clazz, mod.__dict__)
        clazz = mod.__dict__.get('%s' % qname)        
        return clazz

class __MessageModel(Model):
    
    
    payload = properti.ObjectProperty(required=False, length=4294967295)
    pull_flag = properti.BooleanProperty(default=False)    
    pull_time = properti.DateTimeProperty(required=False)    
    # True: consumed successfully  False: consumed failed
    consume_flag = properti.BooleanProperty(default=False)
    consume_time = properti.DateTimeProperty(required=False)    
    consume_error = properti.StringProperty(required=False, length=1000)
    attempts = properti.IntegerProperty(default=0)
    
    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN + '_async'
    
    def complete(self):
        """
            Marks a message as complete.
        """
        query = self.all()
        query.filter("%s =" % Model.DEFAULT_KEYNAME, self.key())
        query.set('consume_flag set', True)
        query.set('consume_time set', kind.utcnow())
        query.set('consume_error set', None)
        query.find_one_and_update(None)
        return True

    def error(self, errormsg=None):
        """
            Note an error processing a job, and return it to the queue.
        """
        query = self.all()
        query.filter("%s =" % Model.DEFAULT_KEYNAME, self.key())
        query.set("consume_flag set", False)
        if errormsg is not None:
            errormsg = errormsg[0:1000]
        query.set("consume_error set", errormsg)
        query.set('consume_time set', kind.utcnow())
        query.set("pull_flag set", False)
        query.set("pull_time set", None)
        query.set("attempts inc", 1)
        query.find_one_and_update(None, new=True)
        return self

    def retry(self):
        """
            Release a message back to the pool. The attempts counter is set to zero.
        """
        query = self.all()
        query.filter("%s =" % self.DEFAULT_KEYNAME, self.key())
        query.set("pull_flag set", False)
        query.set("pull_time set", None)
        query.set("consume_flag set", False)
        query.set("consume_time set", None)
        query.set("consume_error set", None)
        query.set("attempts set", 0)
        query.find_one_and_update(None, new=True)
        return self  
