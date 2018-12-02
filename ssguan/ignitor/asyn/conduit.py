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

import sys

from ssguan.ignitor.asyn import config as asyn_config, logger
from ssguan.ignitor.asyn.error import MaxLengthError
from ssguan.ignitor.base.error import ExceptionWrap
from ssguan.ignitor.utility import parallel, kind
from ssguan.ignitor.base.struct import JsonMixin


class Message(JsonMixin):
    """
        The message object that is sent to the conduit
    """
    def __init__(self, message_type):
        self.__type = message_type        
        self.__content = None
        self.__id = None  # this property is set in Conduit        

    @property
    def type(self):
        return self.__type
    
    @property
    def content(self):
        return self.__content
    
    @property
    def id(self):
        return self.__id
    
    @content.setter
    def content(self, content):
        """
            :param content|jsonobject: object can be jsoned using json.dumps(obj, ensure_ascii=False, cls=ExtJsonEncoder)
        """
        self.__content = content
    
    @id.setter
    def id(self, id1):
        self.__id = id1

    def to_dict(self):
        dic = {}
        dic['type'] = self.__type
        dic['content'] = self.__content
        dic['id'] = self.__id
        return dic

class Processor(object):
    """
        The message processor must extend this class
    """
    def process(self, message):
        """
            Process the message
            :param message|conduit.Message:
            :rtype void
        """
        raise NotImplementedError("Processor.process")

class Conduit(object):
    
    CK_MAX_LENGTH = "max_length"  # the maximum length of one message
    
    def __init__(self, conduit_name, **kwargs):
        self.__conduit_name = conduit_name
        self._kwargs = kwargs
        
    @property
    def name(self):
        return self.__conduit_name    
    
    def produce(self, message):
        """
            Produce the message to this conduit
            :param message|conduit.Message: 
        """
        length = len(kind.obj_to_pickle(message))
        if length > self._kwargs[self.CK_MAX_LENGTH]:
            raise MaxLengthError(self.__conduit_name, self._kwargs[self.CK_MAX_LENGTH], length)
        self.send(message)
    
    def consume(self, message):
        """
            Consume message in this conduit
            :param message|conduit.Message: 
        """        
        job_executor = parallel.funcexector(1, process=False)
        job_executor.start()
        job_executor.submit(self.process, self.__process_success, self.__process_fail, message)        
        job_executor.shutdown(wait=True)
    
    def send(self, message):
        """
            Send message to this conduit
            :param message|conduit.Message: 
        """
        raise NotImplementedError("Conduit.send")
    
    def process(self, message):
        """
            process message
            :param message|Conduit.Message:
        """
        processor = asyn_config.get_processor(message.type).clazz()
        try:
            processor.process(message)            
        except:
            logger.error("process message exception", exc_info=1)
            raise ExceptionWrap(sys.exc_info(), message=message)
        return message
    
    def __process_success(self, message):
        return self.process_success(message)
        
    def __process_fail(self, exc_info):
        exc = exc_info[1]
        message = exc.data['message']
        self.process_fail(exc.message_tb, message)
    
    def process_success(self, message):
        """
            The callback function of Conduit.process is called sucessfully
        """
        raise NotImplementedError("Conduit.process_succeeded")
        
    def process_fail(self, error, message):
        """
            The callback function of Conduit.process is called in failure.
            :param message|Message: conduit.Message instance
            :param error|str the error message with traceback
        """
        raise NotImplementedError("Conduit.process_failed")
    
    def start(self):
        """
            The function must be called to do some init things such as opening the message listener before send message to the conduit.
        """
        raise NotImplementedError("Conduit.init")
    
    def stop(self):
        """
            The function must be called to do some stop things such as closing the message listener while program is existing.
        """
        raise NotImplementedError("Conduit.init")
    
