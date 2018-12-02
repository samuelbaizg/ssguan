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

from ssguan.ignitor.base.error import Error

class MaxLengthError(Error):
    """
        MaxlengthError is to define the error for the message length.
    """
    def __init__(self, conduit_name, max_length, length):
        """
            :param conduit_name|str:  
            :param max_length|int: the maximum length of message in conduit
            :param length|int: the length of message to be sent in conduit
        """
        super(MaxLengthError, self).__init__("The length of message in conduit %s has over the max limits %s > %s " % (conduit_name, length, max_length))
    
    @property
    def code(self):
        return 1030
