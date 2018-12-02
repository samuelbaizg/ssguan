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

from ssguan.ignitor.asyn import config as asyn_config 
from ssguan.ignitor.asyn.conduit import Message


def send_message(message_type, content):
    """
        send asynchronous message
        :param message_type|str: message type
        :param content|object: the object can be converted to json format.
    """
    conduit1 = asyn_config.get_conduit(message_type)
    msg = Message(message_type)
    msg.content = (content)
    conduit1.produce(msg)