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

import copy
import os

from ssguan.ignitor.base import error
from ssguan.ignitor.base.error import CompareError, NoFoundError, InvalidError
from ssguan.ignitor.etl import logger
from ssguan.ignitor.etl.functor import Extractor
from ssguan.ignitor.utility import kind


class JoinET(Extractor):  
    """
        Create the generator through the iterable object.
         :param data|iterable: the iterable object with dict object.
    """
    def __init__(self):
        super(JoinET, self).__init__()
        self.data = None
        
    def _arg_names(self):
        return ('data',)
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.data, "JoinET.data")
        return True
    
    def _extract(self):
        result = [{}] if self.data is None else self.data
        for r in result:
            yield copy.copy(r)

class RangeET(Extractor):    
    """
        Create the generator through number.
        :param column|str: the column name to be created.
        :param start|int: the start index
        :param end|int: the end index
        :param step|int: the step increment from start to end  
    """   
    def __init__(self):
        super(RangeET, self).__init__()
        self.column = None
        self.start = 0
        self.end = 999
        self.step = 1
    
    def _arg_names(self):
        return ('column', 'start', 'end', 'step')
    
    def _validate_args(self, kwargs):        
        error.assert_required(kwargs.column, 'RangeET.column')
        error.assert_required(kwargs.start, 'RangeET.start')
        error.assert_required(kwargs.end, 'RangeET.end')
        error.assert_required(kwargs.step, 'RangeET.step')
        error.assert_type_str(kwargs.column, 'RangeET.column')
        error.assert_type_int(kwargs.start, 'RangeET.start')
        error.assert_type_int(kwargs.end, 'RangeET.end')
        error.assert_type_int(kwargs.step, 'RangeET.step')
        if kwargs.end < kwargs.start:
            raise CompareError('RangeET.start', '<=', 'RangeET.end', kwargs.end)
        return True
    
    def _extract(self):
        values = []
        try:
            values = range(self.start, self.end, self.step)
        except Exception:
            logger.warn("failed to create values by builtin range method.", exc_info=True)
        for i in values:
            item = {self.column: i}
            yield item
    
class ReadET(Extractor):
    """
        Create the generator through reading file one row by one row.
        :param filepath|str: the file path to be read. the extension decides how to parse the file.
        :param unpack|function: the function convert the one row in file to dict.
    """   
    def __init__(self):
        super(ReadET, self).__init__()
        self.filepath = None
        self.unpack = None
    
    def _arg_names(self):
        return ('filepath', 'unpack')
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.filepath, 'ReadET.filepath')
        error.assert_required(kwargs.unpack, 'ReadET.unpack')
        error.assert_type_function(kwargs.unpack, 'ReadET.unpack')
        if not os.path.exists(kwargs.filepath):
            raise NoFoundError('filepath', kwargs.filepath)
        if not os.path.isfile(kwargs.filepath):
            raise InvalidError(kwargs.filepath, "it is not a file object.")
    
    def _extract(self):
        ext = os.path.splitext(self.filepath)
        ext = ext[1][1:] if len(ext) > 0 else ''
        if ext.lower() == 'json':
            g = self._extract_json()
        else:
            g = self._extract_file()
        return g
    
    def _extract_file(self):
        """
            Extract the file one row by one row.
        """
        with open(self.filepath, 'r') as f:
            for line in f:
                r = self.unpack(line)
                yield copy.copy(r)
        
    def _extract_json(self):
        """
            Extract the file by json.
        """
        with open(self.filepath, 'r') as f:
            fstr = f.read()
            json = kind.json_to_object(fstr)
            if isinstance(json, list):
                for item in json:
                    yield self.unpack(item)
            else:
                yield json                    