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

import time

from ssguan.ignitor.utility import parallel


class Bucket(object):

    def __init__(self, rate=1, burst=None):
        """
            traffic flow control with token bucket
        """
        self.__rate = float(rate)
        if burst is None:
            self.__burst = float(rate) * 10
        else:
            self.__burst = float(burst)
        self.__mutex = parallel.create_lock(False)
        self.__bucket = self.__burst
        self.__last_update = time.time()

    def get(self):
        '''Get the number of tokens in bucket'''
        now = time.time()
        if self.__bucket >= self.__burst:
            self.__last_update = now
            return self.__bucket
        bucket = self.__rate * (now - self.__last_update)
        try:
            self.__mutex.acquire()
            if bucket > 1:
                self.__bucket += bucket
                if self.__bucket > self.__burst:
                    self.__bucket = self.__burst
                self.__last_update = now
        finally:
            self.__mutex.release()
        return self.__bucket

    def set(self, value):
        '''Set number of tokens in bucket'''
        self.__bucket = value

    def desc(self, value=1):
        '''Use value tokens'''
        self.__bucket -= value