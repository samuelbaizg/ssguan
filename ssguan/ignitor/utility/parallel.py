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

from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
import contextlib
import threading

"""
    Parallel utilities
"""

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

    def submit(self, fn, success_cb, fail_cb, *args, **kwargs):
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
                self._run_fail(fail_cb, exc_info)
            else:
                self._run_success(success_cb, f.result())
        with self._lock:
            f = self._pool.submit(fn, *args, **kwargs)
            f.add_done_callback(callback)

    def _run_success(self, success_cb, result):
        if success_cb is not None:
            success_cb(result)
        
    def _run_fail(self, failure_cb, exc_info):
        if failure_cb is not None:
            failure_cb(exc_info)

def funcexector(max_workers=10, process=False):
    return FuncExecutor(max_workers, process=process)