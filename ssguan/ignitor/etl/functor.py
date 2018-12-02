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

from ssguan.ignitor.base import error
from ssguan.ignitor.base.struct import Storage
from ssguan.ignitor.etl import logger
from ssguan.ignitor.utility import kind


class Functor(object):
    
    """
        The base class of ETL functor. A functor is to do one thing to change the data in data stream.
    """
    
    @classmethod
    def name(cls):
        """
            Return the init function name in ETLTask.
        """
        return cls.__name__.lower()[:-2]
    
    def class_name(self):
        """
            Return the class name for this functor.
        """
        return self.__class__.__name__
    
    def init(self, **kwargs):
        """
            init this functor using the arguments. it is called once the functor instance is created.
        """        
        self.validate_args(Storage(kwargs))
        for key in self.arg_names():
            if key in kwargs:            
                value = kwargs[key]            
                setattr(self, key, value)
    
    def arg_names(self):
        """
            Return all the argument names of current and base classes for initializing.
        """
        arg_names = []
        if type(self) != Functor:
            arg_names.extend(self._arg_names())
            for parent_class in self.__class__.__bases__:
                arg_names.extend(parent_class().arg_names())
        return arg_names
    
    def validate_args(self, kwargs):
        """
            Valid if all the arguments of init method are valid for current and base functor instances.
            :param kwargs|struct.Storage:
        """
        if type(self) != Functor:
            if isinstance(kwargs, Storage):
                kwargs = Storage(kwargs)            
            for parent_class in self.__class__.__bases__:
                parent_class().validate_args(kwargs)
            self._validate_args(kwargs)
        return True
    
    def process(self, generator):
        """
            Process the data.
            :param generator|generator: the generator contains dict type. 
            :rtype generator: yield data in this method body.
        """
        try:
            g = self._process(generator)
            error.assert_type_generator(g, "the return for %s._process" % self.class_name())
            return g
        except:
            logger.error("Functor %s (%s)." (self.class_name(), str(self.arg_names())), exc_info=1)
        
    def _arg_names(self):
        """
            Return the argument names of current class for initializing.           
        """
        raise NotImplementedError("Functor._arg_names is not implemented.")
    
    
    def _validate_args(self, kwargs):
        """
            Valid if the arguments of init method are valid for current functor instance.
            :param kwargs|struct.Storage' the arguments of init method.
            :rtype bool: Returning True if OK or else raising exception. 
        """
        raise NotImplementedError("Functor._validate_args is not implemented.")
    
    def _process(self, generator):
        """
            Process the data. 
            :param generator|generator: the generator contains dict type. 
            :rtype generator: yield data in this method body.
        """
        raise NotImplementedError("Functor.process is not implemented.")
        
class Extractor(Functor):
    """
        Create a generator by extracting data from all kinds of data sources.
        :param mode: the operator for two generators. the option should be one of MODE_xxx defined in this class.
    """
    MODE_APPEND = '+'  # append one generator to another generator
    MODE_CROSS = '*'  # 
    MODE_MERGE = '|'  # merge two dict
    MODE_MIX = 'mix'
    
    def __init__(self):
        super(Extractor, self).__init__()
        self.mode = self.MODE_APPEND
    
    def _arg_names(self):
        return ('mode',)
    
    def _validate_args(self, kwargs):
        choices = (self.MODE_APPEND, self.MODE_CROSS, self.MODE_MERGE, self.MODE_MIX)
        error.assert_required(kwargs.mode, "Extractor.mode")
        error.assert_in(kwargs.mode, choices, "Extractor.mode")
        return True
            
    def _process(self, generator):
        g2 = self._extract()
        if generator is None:
            return g2
        else:            
            if self.mode == self.MODE_APPEND:
                return kind.generator_append(generator, g2)            
            elif self.mode == self.MODE_MERGE:
                return kind.generator_merge(generator, g2)
            elif self.mode == self.MODE_CROSS:
                return kind.generator_cross(generator, g2)
            else:
                return kind.generator_mix(generator, g2)
    
    def _extract(self):
        """
            Create generator.
            :rtype generator: yield data in this method body
        """
        raise NotImplementedError("Extractor.extract is not implemented.")
            
class Transformer(Functor):
    
    """
        Transform the data in data stream.
    """    
    def __init__(self):
        super(Transformer, self).__init__()
        
    def _arg_names(self):
        return ()
    
    def _validate_args(self, kwargs):
        pass
    
    def _process(self, generator):
        """
            Override this function when transform the whole data in generator.
        """
        for data in generator:
                yield self._transform(data)
    
    def _transform(self, data):
        """
            Transform data in the data stream.
            Override this function when transform one column.
            :param data|dict: the element to be transformed.
            :rtype dict: the data after being transformed.
        """
        pass

class Filter(Functor):
    
    """
        Filter the data in data stream.
        :param reverse: Using the reverse result of self.filter when processing the data stream.
    """    
    
    def __init__(self):
        super(Filter, self).__init__()
        self.reverse = False
        
    def _arg_names(self):
        return ('reverse',)
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.reverse, "Filter.reverse")
        error.assert_type_bool(kwargs.reverse, "Filter.reverse")
    
    def _process(self, generator):
        for data in generator:
            result = self.keep(data)
            if result and not self.reverse:
                yield data
            if not result and self.reverse:
                yield data
    
    def _keep(self, data):
        """
            Check if the data should be kepted in the data scream.
            :param data|dict: the element to be filtered.
            :rtype bool: True means the data will kept in the data sream. False means the data will be removed from the data stream.
        """
        raise NotImplementedError("Filter.keep is not implemented.")

class Loader(Functor):
    
    """
        Persist the data stream into other stoarge such as db, file and so on.        
    """    
    
    def __init__(self):
        super(Loader, self).__init__()
        
    def _arg_names(self):
        return ()
    
    def _validate_args(self, kwargs):
        pass
    
    def _process(self, generator):
        for data in generator:
            try:
                self._load(data)
            except:
                self._failed(data, sys.exc_info)

    
    def _load(self, data):
        """
            Persist the data.            
        """
        raise NotImplementedError("Loader.load is not implemented.")
    
    def _fail(self, data, tb):
        """
            Do something when exception is raised by self.load
            :param data|dict: the element to be persisted.
            :param tb|tuple: the exception info. (type,value,traceback)
        """
