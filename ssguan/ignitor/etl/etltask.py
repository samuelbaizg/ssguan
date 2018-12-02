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

import inspect

from ssguan.ignitor.etl import functor, etfunctor, tffunctor, ftfunctor, \
    ldfunctor, logger
from ssguan.ignitor.etl.functor import Functor
from ssguan.ignitor.utility import kind, parallel

class Task(object):
    
    def __init__(self, task_name):
        self.__task_name = task_name
        self.__functors = []
        self.__add_functor_functions()
        self.__data = None
        self.__lock = parallel.create_lock()
    
    def __len__(self):
        return len(self.__functors)
    
    def __iter__(self):
        for r in self.query():
            yield r
    
    def __add_functor_functions(self):
        """
            Add all functions of initializing the functor to this task.            
        """
        
        def build_func_str(module_name, functor_class):
            
            def build_arg_str(key, value):
                if kind.is_str(value):
                    value = "'%s'" % (value)
                return '%s=%s' % (key, value)
            
            func_str = '''
def %s(%s):
    from ssguan.ignitor.etl.%s import %s
    self.append_functor(%s, %s)
    return self
'''         
            functor_name = functor_class.__name__
            functor_inst = functor_class()
            priv_func_name = '__append_%s' % kind.str_lower_first(functor_name)
            argspec = ','.join([build_arg_str(k, functor_inst.__dict__[k]) for k in functor_inst.arg_names()])
            args = ",".join(['%s=%s' % (k, k) for k in functor_inst.arg_names()])
            func_str = func_str % (priv_func_name, argspec, module_name, functor_name, functor_name, args)
            return (functor_inst.name(), priv_func_name, func_str)
            
        
        def add_functions(module_name, module):
            def base_functor_classes():
                bases = []
                for functor_class in functor.__dict__.values():
                    if inspect.isclass(functor_class) and issubclass(functor_class, Functor):
                        bases.append(functor_class)
                return bases
            
            for name, functor_class in module.__dict__.items():
                try:
                    if not inspect.isclass(functor_class):
                        continue
                    if not issubclass(functor_class, Functor):
                        continue
                    if functor_class in base_functor_classes():
                        continue
                    (pub_func_name, priv_func_name, func_str) = build_func_str(module_name, functor_class)
                    exec(func_str, locals())
                    func = locals()[priv_func_name]
                    setattr(self, pub_func_name, func)
                except BaseException as e:
                    logger.error("functor_class:%s, func_str:%s" % (functor_class, func_str), exc_info=1)
                    raise e
                finally:
                    (pub_func_name, priv_func_name, func_str) = (None, None, None)
                
        
        add_functions('etfunctor', etfunctor)
        add_functions('tffunctor', tffunctor)
        add_functions('ftfunctor', ftfunctor)
        add_functions('ldfunctor', ldfunctor)
        return self
    
    @property
    def name(self):
        return self.__task_name
    
    def append_functor(self, functor_class, **kwargs):
        """
            Add functor to this task.
            :param functor_class|Functor sub-classes: 
            :param kwargs|dict: the init arguments of function Functor.init
            
        """
        functor = functor_class()    
        functor.init(**kwargs)
        self.__functors.append(functor)
        return self
        
    def query(self, force=False):
        """
            Execute functors to create the data scream.
            :param force|bool: Execute functors only once if force == False. Execute again if force == True. 
            :rtype generator:
        """
        try:
            self.__lock.acquire()        
            if force or self.__data is None:
                generator = None
                for functor1 in self.__functors:
                    generator = functor1.process(generator)
                self.__data = [] if generator is None else generator
        finally:
            self.__lock.release()
        return self.__data
    
    def next(self):
        """
            Return next element.
        """
        try:
            return self.query().__next__()
        except StopIteration:
            return None

def create_task(task_name='etl'):
    """
        Create a etl task
        :param task_name|str: Task Name
        :rtype ETLTask:
    """
    return Task(task_name)
