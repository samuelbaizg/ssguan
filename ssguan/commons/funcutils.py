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

import contextlib
import functools
import re
from threading import local as threadlocal
import threading
import time
import traceback
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
import six


class RWLock(object):
    """
    Classic implementation of reader-writer lock with preference to writers.

    Readers can access a resource simultaneously.
    Writers get an exclusive access.

    API is self-descriptive:
        reader_enters()
        reader_leaves()
        writer_enters()
        writer_leaves()
    """
    def __init__(self):
        self.mutex = threading.RLock()
        self.can_read = threading.Semaphore(0)
        self.can_write = threading.Semaphore(0)
        self.active_readers = 0
        self.active_writers = 0
        self.waiting_readers = 0
        self.waiting_writers = 0

    def reader_enters(self):
        with self.mutex:
            if self.active_writers == 0 and self.waiting_writers == 0:
                self.active_readers += 1
                self.can_read.release()
            else:
                self.waiting_readers += 1
        self.can_read.acquire()

    def reader_leaves(self):
        with self.mutex:
            self.active_readers -= 1
            if self.active_readers == 0 and self.waiting_writers != 0:
                self.active_writers += 1
                self.waiting_writers -= 1
                self.can_write.release()

    @contextlib.contextmanager
    def reader(self):
        self.reader_enters()
        try:
            yield
        finally:
            self.reader_leaves()

    def writer_enters(self):
        with self.mutex:
            if self.active_writers == 0 and self.waiting_writers == 0 and self.active_readers == 0:
                self.active_writers += 1
                self.can_write.release()
            else:
                self.waiting_writers += 1
        self.can_write.acquire()

    def writer_leaves(self):
        with self.mutex:
            self.active_writers -= 1
            if self.waiting_writers != 0:
                self.active_writers += 1
                self.waiting_writers -= 1
                self.can_write.release()
            elif self.waiting_readers != 0:
                t = self.waiting_readers
                self.waiting_readers = 0
                self.active_readers += t
                while t > 0:
                    self.can_read.release()
                    t -= 1

    @contextlib.contextmanager
    def writer(self):
        self.writer_enters()
        try:
            yield
        finally:
            self.writer_leaves()

@contextlib.contextmanager
def contextmanager_dummy():
    """A context manager that does nothing special."""
    yield

def create_rlock(process=False):
    """Creates a reentrant lock object."""
    if process:
        from multiprocessing import RLock as rlockp
        return rlockp()
    else:
        from threading import RLock as rlockt
        return rlockt()
    
def create_lock(process=False):
    """Creates a reentrant lock object."""
    if process:
        from multiprocessing import Lock as lockp
        return lockp()
    else:
        from threading import Lock as lockt
        return lockt()

    
def wrap_func(func, *args, **kwargs):
    wrapper = functools.partial(func, *args, **kwargs)
    try:
        functools.update_wrapper(wrapper, func)
    except AttributeError:
        # func already wrapped by functools.partial won't have
        # __name__, __module__ or __doc__ and the update_wrapper()
        # call will fail.
        pass
    return wrapper

def import_module(path):
    """
        import moddule from string
        :param str funcpath: the string of absolute path a module
    """
    try:
        if "." in path:
            modpath, hcls = path.rsplit('.', 1)
            mod = __import__(modpath, None, None, [''])
            mod = getattr(mod, hcls)
        else:
            mod = __import__(path, None, None, [''])
    except:
        mod = None        
    return mod

def get_function_path(function, bound_to=None):
    """Get received function path (as string), to import function later
    with `import_string`.
    """
    if isinstance(function, six.string_types):
        return function

    # static and class methods
    if hasattr(function, '__func__'):
        real_function = function.__func__
    elif callable(function):
        real_function = function
    else:
        return function

    func_path = []

    module = getattr(real_function, '__module__', '__main__')
    if module:
        func_path.append(module)

    if not bound_to:
        try:
            bound_to = six.get_method_self(function)
        except AttributeError:
            pass

    if bound_to:
        if isinstance(bound_to, six.class_types):
            func_path.append(bound_to.__name__)
        else:
            func_path.append(bound_to.__class__.__name__)

    func_path.append(real_function.__name__)
    return '.'.join(func_path)


class FuncExecutor(object):
    """
        Run functions in thread or process.
    """
    _lock = None

    def __init__(self, max_workers, process=False):
        if process:
            self._pool = ProcessPoolExecutor(max_workers)
        else:
            self._pool = ThreadPoolExecutor(max_workers)
        self._process = process
        self._max_workers = max_workers

    def start(self):
        """
        Start this executor.
        """
        self._lock = create_rlock(self._process)

    def shutdown(self, wait=True):
        """
        Shuts down this executor.
        :param bool wait: ``True`` to wait until all submitted functions
            have been executed
        """
        self._pool.shutdown(wait)

    def submit(self, fn, success_cb, failure_cb, *args, **kwargs):
        """
        Submits function for execution.

        :param fn|function: function to execute        
        :raises MaxInstancesReachedError: if the maximum number of
            allowed instances for this job has been reached
        """
        assert self._lock is not None, 'This executor has not been started yet'
        def callback(f):
            exc, tb = (f.exception_info() if hasattr(f, 'exception_info') else
                       (f.exception(), getattr(f.exception(), '__traceback__', None)))
            exc_info = (exc.__class__, exc, tb)
            if exc:
                self._run_failure(failure_cb, exc_info)
            else:
                self._run_success(success_cb, f.result())
        with self._lock:
            f = self._pool.submit(fn, *args, **kwargs)
            f.add_done_callback(callback)

    def _run_success(self, success_cb, result):
        if success_cb is not None:
            success_cb(result)
        
    def _run_failure(self, failure_cb, exc_info):
        if failure_cb is not None:
            failure_cb(exc_info)

def funcexector(max_workers=10, process=False):
    return FuncExecutor(max_workers, process=process)

class ThreadedDict(threadlocal):
    """
    Thread local storage.
    
        >>> d = ThreadedDict()
        >>> d.x = 1
        >>> d.x
        1
        >>> import threading
        >>> def f(): d.x = 2
        ...
        >>> t = threading.Thread(target=f)
        >>> t.start()
        >>> t.join()
        >>> d.x
        1
    """
    _instances = set()
    
    def __init__(self):
        ThreadedDict._instances.add(self)
        
    def __del__(self):
        ThreadedDict._instances.remove(self)
        
    def __hash__(self):
        return id(self)
    
    def clear_all():
        """Clears all ThreadedDict instances.
        """
        for t in list(ThreadedDict._instances):
            t.clear()
    clear_all = staticmethod(clear_all)
    
    # Define all these methods to more or less fully emulate dict -- attribute access
    # is built into threading.local.

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    has_key = __contains__
        
    def clear(self):
        self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def items(self):
        return self.__dict__.items()

    def iteritems(self):
        return self.__dict__.iteritems()

    def keys(self):
        return self.__dict__.keys()

    def iterkeys(self):
        return self.__dict__.iterkeys()

    iter = iterkeys

    def values(self):
        return self.__dict__.values()

    def itervalues(self):
        return self.__dict__.itervalues()

    def pop(self, key, *args):
        return self.__dict__.pop(key, *args)

    def popitem(self):
        return self.__dict__.popitem()

    def setdefault(self, key, default=None):
        return self.__dict__.setdefault(key, default)

    def update(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __repr__(self):
        return '<ThreadedDict %r>' % self.__dict__

    __str__ = __repr__

class Memoize:
    """
    'Memoizes' a function, caching its return values for each input.
    If `expires` is specified, values are recalculated after `expires` seconds.
    If `background` is specified, values are recalculated in a separate thread.
    
        >>> calls = 0
        >>> def howmanytimeshaveibeencalled():
        ...     global calls
        ...     calls += 1
        ...     return calls
        >>> fastcalls = memoize(howmanytimeshaveibeencalled)
        >>> howmanytimeshaveibeencalled()
        1
        >>> howmanytimeshaveibeencalled()
        2
        >>> fastcalls()
        3
        >>> fastcalls()
        3
        >>> import time
        >>> fastcalls = memoize(howmanytimeshaveibeencalled, .1, background=False)
        >>> fastcalls()
        4
        >>> fastcalls()
        4
        >>> time.sleep(.2)
        >>> fastcalls()
        5
        >>> def slowfunc():
        ...     time.sleep(.1)
        ...     return howmanytimeshaveibeencalled()
        >>> fastcalls = memoize(slowfunc, .2, background=True)
        >>> fastcalls()
        6
        >>> timelimit(.05)(fastcalls)()
        6
        >>> time.sleep(.2)
        >>> timelimit(.05)(fastcalls)()
        6
        >>> timelimit(.05)(fastcalls)()
        6
        >>> time.sleep(.2)
        >>> timelimit(.05)(fastcalls)()
        7
        >>> fastcalls = memoize(slowfunc, None, background=True)
        >>> threading.Thread(target=fastcalls).start()
        >>> time.sleep(.01)
        >>> fastcalls()
        9
    """
    def __init__(self, func, expires=None, background=True): 
        self.func = func
        self.cache = {}
        self.expires = expires
        self.background = background
        self.running = {}
    
    def __call__(self, *args, **keywords):
        key = (args, tuple(keywords.items()))
        if not self.running.get(key):
            self.running[key] = threading.Lock()
        def update(block=False):
            if self.running[key].acquire(block):
                try:
                    self.cache[key] = (self.func(*args, **keywords), time.time())
                finally:
                    self.running[key].release()
        
        if key not in self.cache: 
            update(block=True)
        elif self.expires and (time.time() - self.cache[key][1]) > self.expires:
            if self.background:
                threading.Thread(target=update).start()
            else:
                update()
        return self.cache[key][0]

re_compile = Memoize(re.compile)  # @@ threadsafe?
re_compile.__doc__ = """A memoized version of re.compile."""

class _re_subm_proxy:
    def __init__(self): 
        self.match = None
    def __call__(self, match): 
        self.match = match
        return ''

def re_subm(pat, repl, string):
    """
    Like re.sub, but returns the replacement _and_ the match object.
    
        >>> t, m = re_subm('g(oo+)fball', r'f\\1lish', 'goooooofball')
        >>> t
        'foooooolish'
        >>> m.groups()
        ('oooooo',)
    """
    compiled_pat = re_compile(pat)
    proxy = _re_subm_proxy()
    compiled_pat.sub(proxy.__call__, string)
    return compiled_pat.sub(repl, string), proxy.match

def format_exc_info(exc_info):
    error_class = exc_info[1]
    tb_message = format_traceback(exc_info[2])
    return "%s\n%s" % (error_class.message, tb_message)

def format_traceback(traceback1):
    return "".join(traceback.format_tb(traceback1))

