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


class IllegalWordError(Error):
    def __init__(self, label, illegalword):
        super(IllegalWordError, self).__init__("{{label}} includes the illegal word {{illegalword}}", label=label, illegalword=illegalword)
    @property
    def code(self):
        return 1040   
    
class LinkedError(Error):
    def __init__(self, mainlabel, linklabel):
        super(LinkedError, self).__init__("{{mainlabel}} is related to {{linklabel}}.", mainlabel=mainlabel, linklabel=linklabel)
    @property
    def code(self):
        return 1041    

class UniqueError(Error):
    def __init__(self, label, value):
        super(UniqueError, self).__init__("The value {{value}} of {{label}} has existed." , label=label, value=value)
    @property
    def code(self):
        return 1042    
    
class UpdateError(Error):
    """
        UpdateError is to define the error for update.
    """
    def __init__(self, message, *args):
        super(UpdateError, self).__init__(message, *args)
    
    @property
    def code(self):
        return 1043

class DataExpiredError(Error):
    def __init__(self):
        super(DataExpiredError, self).__init__("The local data is expired, please refresh data or UI after reloading latest data from server.")
    
    @property
    def code(self):
        return 1044