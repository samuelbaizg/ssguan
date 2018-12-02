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

import locale


def kilostr_to_int(money,times=1):
    """
        Return the int value of the kilo float string.
        @param money|string: the string to be converted
        @param times|int: how many times to be multiplied by  
    """    
    locale.setlocale(locale.LC_NUMERIC, 'English_US')
    to = locale.atof(money)    
    return int(to * times)

def kilostr_to_float(money,times=1):
    """
        Return the float value of the kilo float string.
        @param money|string: the string to be converted
        @param times|int: how many times to be multiplied by  
    """    
    locale.setlocale(locale.LC_NUMERIC, 'English_US')
    to = locale.atof(money)    
    return float(to * times)