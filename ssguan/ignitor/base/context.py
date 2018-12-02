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
import threading

"""
    The module to hold the global variables with respect to current thread. 
"""

__global_data = threading.local()

def set_attr(name, value):
    """
      Set global data to the current thread.
      :param name|string: the name of the data
      :param name|object: the value of the data
      :return: void
    """
    setattr(__global_data, name, value)
    
def get_attr(name):
    """
      Get global data from the current thread.
      :param name|string: the name of the data
      :return: the global data with the name
    """
    if hasattr(__global_data, name):
        return getattr(__global_data, name)
    else:
        return None

USER_TOKEN_NAME = 'USER_TOKEN'

def set_token(token):
    """
        Set the curent user credential of current thread
        @param token|ignitor.auth.model.Token
    """
    set_attr(USER_TOKEN_NAME, token)
def get_token():
    """
        Return the curent user credential of current thread
        :rtype: the instance of ignitor.auth.model.Token
    """
    return get_attr(USER_TOKEN_NAME)

def get_user_id():
    """
        Return the curent user credential of current thread
        :rtype: str
    """
    token = get_token()
    return token.user_id if token is not None else None
    
