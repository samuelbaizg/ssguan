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

class BaseFS(object):
    
    def __init__(self, fsinfo):
        """
        :param maxsize|float: unit is megabytes
        :param overwrite|Bool: True means overwrite the existed file with the same path, or else no.
        """
        self._fsinfo = fsinfo
    
    @property
    def fsinfo(self):
        return self._fsinfo
            
    def save_file(self, filepath, content):        
        """
            Save file to the file system.
            :param filepath|str: the relative file path to the root path in device.  eg. aa/bb/c.csv
            :param content|str or bytes: the file content to be saved.
        """
        raise NotImplementedError('sub-classes of FS must provide an save_file() method')
    
    def read_file(self, filepath):
        """
            Read file from the file system.
            :param filepath|str: the relative file path to the root path in device.  eg. aa/bb/c.csv
        """
        raise NotImplementedError('sub-classes of FS must provide an read_file() method')
    
    def delete_file(self, filepath):
        """
            Delete file from the file system.
            :param filepath|str: the relative file path to the root path in device.  eg. aa/bb/c.csv
        """
        raise NotImplementedError('sub-classes of FS must provide an delete_file() method')
    
    def has_file(self, filepath):        
        """
            Check if the file system has the file.
            :param filepath: the relative file path to the root path in device. eg. aa/bb/c.csv
        """
        raise NotImplementedError('sub-classes of FS must provide an has_file() method')
    
    