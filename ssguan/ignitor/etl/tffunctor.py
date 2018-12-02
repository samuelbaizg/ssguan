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

import re

from ssguan.ignitor.base import error
from ssguan.ignitor.etl.functor import Transformer
from ssguan.ignitor.utility import kind
from ssguan.ignitor.base.error import RequiredError



class SetTF(Transformer):
    
    """
        Set the value to the specified column.
         :param column|str or dict: the column name to be set.
         :param value|object: the value to be set.
    """
    def __init__(self):
        super(SetTF, self).__init__()
        self.column = None
        self.value = None
        
    def _arg_names(self):
        return ('column', 'value')
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, "SetTF.column")
        error.assert_in(type(kwargs.column), (str, dict), "SetTF.column")
        return True
    
    def _transform(self, data):
        if isinstance(self.column, dict):            
            for key, value in self.column.items():
                data[key] = value
        else:
            data[self.column] = self.value
        return data

class MoveTF(Transformer):
    
    """
        Move the column in dict from one column to the other column.
         :param old|str: the column name to be removed.
         :param new|str: the column name of destination.
    """
    def __init__(self):
        super(MoveTF, self).__init__()
        self.old = None
        self.new = None
        
    def _arg_names(self):
        return ('old', 'new')
        
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.old, 'MoveTF.old')
        error.assert_required(kwargs.new, 'MoveTF.new')
        error.assert_type_str(kwargs.old, 'MoveTF.old')
        error.assert_type_str(kwargs.new, 'MoveTF.new')
        error.assert_not_equal(kwargs.old, kwargs.new, 'MoveTF.old', 'MoveTF.new')
        
    def _transform(self, data):
        if self.old in data:
            data[self.new] = data[self.old]
            del data[self.old]
        else:
            data[self.new] = None
        return data

class CopyTF(Transformer):
    
    """
        Copy the column in dict from one column to the other column.
         :param old|str: the column name to be copied.
         :param new|str: the column name of destination.
    """
    def __init__(self):
        super(CopyTF, self).__init__()
        self.old = None
        self.new = None
        
    def _arg_names(self):
        return ('old', 'new')
        
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.old, 'CopyTF.old')
        error.assert_required(kwargs.new, 'CopyTF.new')
        error.assert_type_str(kwargs.old, 'CopyTF.old')
        error.assert_type_str(kwargs.new, 'CopyTF.new')
        error.assert_not_equal(kwargs.old, kwargs.new, 'CopyTF.old', 'CopyTF.new')
        
    def _transform(self, data):
        if self.old in data:
            data[self.new] = data[self.old]
        else:
            data[self.new] = None
        return data
            
class RemoveTF(Transformer):
    
    """
        Delete one column in dict.
         :param column|str, list: the column name or the column list to be removed
    """
    def __init__(self):
        super(RemoveTF, self).__init__()
        self.columns = None
    
    def _arg_names(self):
        return ('columns',)
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.columns, 'RemoveTF.columns')
        error.assert_in(type(kwargs.columns), (str, list), 'RemoveTF.columns')
        
    def _transform(self, data):
        if type(self.columns) == list:
            for col in self.columns:
                data[col] = None
                del data[col]
        else:            
            data[self.columns] = None
            del data[self.columns]
        return data    

class SplitTF(Transformer):
    
    """
        Split the column into list.
        :param column|str: the target column.
        :param seperator|str: the seperator.
    """
    def __init__(self):
        super(SplitTF, self).__init__()
        self.column = None
        self.seperator = None
        
    def _arg_names(self):
        return ('column', 'seperator')
        
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'SplitTF.column')
        error.assert_required(kwargs.seperator, 'SplitTF.seperator')
        error.assert_type_str(kwargs.column, 'SplitTF.column')
        error.assert_type_str(kwargs.seperator, 'SplitTF.seperator')            
        
    def _transform(self, data):
        value = re.split(self.seperator, data[self.column])
        data[self.column] = value
        return data
    
class ReplaceTF(Transformer):
    
    """
        Replace the value of target column through str.replace function.        
        :param column|str: the target column to be replaced.
        :param old|str: the old value to be replaced.
        :param new|str: the new value.
    """   
    def __init__(self):
        super(ReplaceTF, self).__init__()        
        self.column = None
        self.old = None       
        self.new = None        
        
    def _arg_names(self):
        return ('column', 'old', 'new')
        
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'ReplaceTF.column')
        error.assert_required(kwargs.old, 'ReplaceTF.old')
        error.assert_required(kwargs.new, 'ReplaceTF.new')
        error.assert_type_str(kwargs.column, 'ReplaceTF.column')
        error.assert_type_str(kwargs.old, 'ReplaceTF.old')
        error.assert_type_str(kwargs.new, 'ReplaceTF.new')
        
    def _transform(self, data):
        value = data[self.column]
        result = value.replace(self.old, self.new)
        data[self.column] = result
        return data
    
class SubTF(Transformer):
    
    """
        Search and replace the value of target column through re.sub function.        
        :param column|str: the target column to be searched and replaced.
        :param pattern|str: the regex pattern.
        :param value|str: the new value.
    """
   
    def __init__(self):
        super(SubTF, self).__init__()        
        self.column = None        
        self.pattern = None
        self.value = None
        
    def _arg_names(self):
        return ('column', 'pattern', 'value')
        
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'SubTF.column')
        error.assert_required(kwargs.pattern, 'SubTF.pattern')
        error.assert_type_str(kwargs.column, 'SubTF.column')
        error.assert_type_str(kwargs.pattern, 'SubTF.pattern')
        
    def _transform(self, data):
        value = data[self.column]
        result = re.sub(self.pattern, self.value, value)
        data[self.column] = result
        return data

class FindallTF(Transformer):
    
    """
        Search the value in target column through re.findall function.
        :param column|str: the column name to be searched.
        :param pattern|str: the regex pattern.                       
    """
   
    def __init__(self):
        super(FindallTF, self).__init__()
        self.column = None
        self.pattern = None        
        
    def _arg_names(self):
        return ('column', 'pattern')
        
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'FindallTF.column')
        error.assert_required(kwargs.pattern, 'FindallTF.pattern')        
        error.assert_type_str(kwargs.column, 'FindallTF.column')
        error.assert_type_str(kwargs.pattern, 'FindallTF.pattern')        
        
    def _transform(self, data):        
        if self.column in data and data[self.column] is not None:
            regex = re.compile(self.pattern)
            items = re.findall(regex, data[self.column])
            data[self.column] = items
        return data

class FindnumTF(Transformer):
    
    """
        Search the number in target column through re.findall function.                
        :param column|str: the column name to be searched.        
    """
    
    def __init__(self):
        super(FindnumTF, self).__init__()
        self.column = None
        self.pattern = '(-?\\d+)(\\.\\d+)?'        
    
    def _arg_names(self):
        return ('column',)
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'FindnumTF.column')
        error.assert_type_str(kwargs.column, 'FindnumTF.column')
        
    def _transform(self, data):        
        if self.column in data and data[self.column] is not None:
            regex = re.compile(self.pattern)
            items = re.findall(regex, data[self.column])
            data[self.column] = items
        return data

class StripTF(Transformer):
    
    """
         Remove whitespace in leading and trailing, if chars is given and not None, remove characters in chars instead.
        :param column|str,list: the column names to be stripped. 
        :param chars|str: default = None 
        :param mode|str: one of LSTRIP, RSTRIP, STRIP. default = STRIP
    """
    
    MODE_LSTRIP = 'LSTRIP'  # strip head
    MODE_RSTRIP = 'RSTRIP'  # strip tail
    MODE_STRIP = 'STRIP'  # strip head and tail 
    
    def __init__(self):
        super(StripTF, self).__init__()        
        self.columns = None                
        self.chars = None
        self.mode = self.MODE_STRIP
        
    def init(self, **kwargs):
        if kwargs['mode'] is None:
            kwargs['mode'] = self.MODE_STRIP
        Transformer.init(self, **kwargs)
        
    def _arg_names(self):
        return ('columns', 'chars', 'mode')
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.columns, 'StripTF.columns')
        error.assert_required(kwargs.chars, 'StripTF.chars')
        error.assert_required(kwargs.mode, 'StripTF.mode')        
        error.assert_in(type(kwargs.columns), (str, list), 'StripTF.columns')
        error.assert_type_str(kwargs.chars, 'StripTF.chars')
        error.assert_in(kwargs.mode, (self.MODE_LSTRIP, self.MODE_RSTRIP, self.MODE_STRIP), 'StripTF.mode')
        
    def _transform(self, data):
        
        def strip(column):            
            if column in data:
                value = data[column]
                if self.mode == self.MODE_STRIP:
                    value = value.strip(self.chars)
                elif self.mode == self.MODE_LSTRIP:
                    value = value.lstrip(self.chars)
                else:
                    value = value.rstrip(self.chars)
                data[column] = value
                
        if type(self.columns) == list:
            for column in self.columns:
                strip(column)
        else:
            strip(self.columns)
        return data

class ElicitTF(Transformer):
    
    """
        sub string with 'left' and ends with 'right' from string
        :param column|str: the column name to be elicit 
        :param left|str: the left string
        :param right|str: the right string
        :param mode|str: if the substring includes start and end. the value is one of MODE_*.  default = MODE_NO_MARGIN. 
    """
    
    MODE_NO_MARGIN = 'NO_MARGIN'  # does not include the 'left' and 'right'
    MODE_MARGIN = 'MARGIN'  # include the 'left' and 'right'
    MODE_MARGIN_LEFT = 'MARGIN_LEFT'  # include 'left'
    MODE_MARGIN_RIGHT = 'MARGIN_RIGHT'  # include 'right'
    
    def __init__(self):
        super(ElicitTF, self).__init__()        
        self.column = None                
        self.left = None
        self.right = None
        self.mode = self.MODE_NO_MARGIN
    
    def init(self, **kwargs):
        if kwargs['mode'] is None:
            kwargs['mode'] = self.MODE_NO_MARGIN
        Transformer.init(self, **kwargs)
    
    def _arg_names(self):
        return ('column', 'left', 'right', 'mode')
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'ElicitTF.column')  
        error.assert_required(kwargs.mode, 'ElicitTF.mode')
        error.assert_type_str(kwargs.left, 'ElicitTF.left')
        error.assert_type_str(kwargs.right, 'ElicitTF.right')
        if kind.str_is_empty(kwargs.left) and kind.str_is_empty(kwargs.right):
            raise RequiredError("ElicitTF.left or ElicitTF.right")
        error.assert_type_str(kwargs.column, 'ElicitTF.column')
        error.assert_type_str(kwargs.mode, 'ElicitTF.mode')
        error.assert_in(kwargs.mode, (self.MODE_NO_MARGIN, self.MODE_MARGIN, self.MODE_MARGIN_LEFT, self.MODE_MARGIN_RIGHT), 'ElicitTF.mode')
    
    def _transform(self, data):
        value = data[self.column]
        left = value.find(self.left)
        if left != -1:
            right = value.rfind(self.right, left)
            if right != -1:                    
                if self.mode == self.MODE_NO_MARGIN:
                    left += len(self.left)
                elif self.mode == self.MODE_MARGIN:
                    right += len(self.right)
                elif self.mode == self.MODE_MARGIN_LEFT:
                    pass
                elif self.mode == self.MODE_MARGIN_RIGHT:
                    left += len(self.left)
                    right += len(self.right)
                value = value[left:right]
                data[self.column] = value
        return data
    
class MapTF(Transformer):
    
    """
        Map data stream by function. if column is not None, just map the column.
        :param function|function:  the map function. if column is None, the argument is element in generator, the argument is value of data[column] instead. 
        :param columns|str,list: the column names to be map. default = None.
    """
    
    def __init__(self):
        super(MapTF, self).__init__()     
        self.function = None   
        self.columns = None                
    
    def _arg_names(self):
        return ('function', 'columns')
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.function, 'MapTF.function')
        error.assert_type_function(kwargs.function, 'MapTF.function')
        if kwargs.columns is not None:
            error.assert_in(type(kwargs.columns), (str, list), 'MapTF.columns')
    
    def _transform(self, data):
        def map_column(column):
            if column in data:
                value = data[column]
                value = self.function(value)
                data[column] = value
        if type(self.columns) == list:
            for column in self.columns:
                map_column(column)
        else:
            map_column(self.columns)
            
    def _process(self, generator):
        if self.columns is None:
            map(self.function, generator)
        else:
            for data in generator:
                yield self._transform(data) 

class MergeTF(Transformer):
    
    """
        Merge the items in one 'dict' column to main dict in data stream.         
        :param column|str: the column name to be merged.
        :param keys|str,list: the dict keys to be merged. if keys is None, all key will be mreged into main dict.
    """
    
    def __init__(self):
        super(MergeTF, self).__init__()
        self.column = None
        self.keys = None
    
    def _arg_names(self):
        return ('column', 'keys')
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'MergeTF.column')
        error.assert_type_str(kwargs.column, 'MergeTF.column')
        if kwargs.keys is not None:
            error.assert_in(type(kwargs.keys), (str, list), 'MergeTF.keys')
    
    def _transform(self, data):
        value = data[self.column]            
        kind.dict_merge(data, value, self.keys)
        return data

class ListTF(Transformer):
    
    """
        Drill up list data.  eg. if the data stream is [{'a':[1,2]}], returning the new data stream [{'a':1},{'a':2}] after drilled up.       
        :param column: the column name to be drilled up.        
    """
    
    def __init__(self):
        super(ListTF, self).__init__()
        self.column = None
    
    def _arg_names(self):
        return ('column',)
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'ListTF.column')
        error.assert_type_str(kwargs.column, 'ListTF.column')
    
    def _process(self, generator):
        for data in generator:
            d2 = {}
            for r in data[self.column]:
                d2[self.column] = r
                yield d2
    
class DictTF(Transformer):
    
    """
        Drill up dict data.  eg. if the data stream is [{'a':{'a1':1,'a2':2}}], returning the new data stream [{'a1':1},{'a2':2}] after drilled up.       
        :param column: the column name to be drilled up.        
    """
    
    def __init__(self):
        super(DictTF, self).__init__()
        self.column = None
    
    def _arg_names(self):
        return ('column',)
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.column, 'DictTF.column')
        error.assert_type_str(kwargs.column, 'DictTF.column')
    
    def _process(self, generator):
        for data in generator:
            d2 = {}
            for key, value in data[self.column].items():
                d2[key] = value
            yield d2

class TakeTF(Transformer):
    
    """
        Take a part of the data stream from skip to skip+limit.
        :param limit: the quantity to take.
        :param skip:  the start index to take.        
    """
    
    def __init__(self):
        super(TakeTF, self).__init__()
        self.limit = 10
        self.skip = 0
    
    def _arg_names(self):
        return ('limit', 'skip')
    
    def _validate_args(self, kwargs):
        error.assert_required(kwargs.limit, 'TakeTF.limit')
        error.assert_type_int(kwargs.limit, 'TakeTF.limit')
        error.assert_required(kwargs.skip, 'TakeTF.skip')
        error.assert_type_int(kwargs.skip, 'TakeTF.skip')
    
    def _process(self, generator):
        i = 0
        for r in generator:
            i += 1
            if i < self.skip:
                continue
            if i > self.limit + self.skip:
                break
            yield r

class LastTF(Transformer):
    
    """
        Take a part of the data stream from skip to skip+limit.
        :param limit|int: the quantity to take.
        :param skip|int:  the start index to take.        
    """
    
    def __init__(self):
        super(LastTF, self).__init__()
    
    def _arg_names(self):
        return ()
    
    def _validate_args(self, kwargs):
        pass
    
    def _process(self, generator):
        r0 = None
        while True:
            try:
                x = next(generator)
                r0 = x
            except StopIteration:
                break
        yield r0

