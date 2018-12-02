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

import os

from ssguan.ignitor.base.error import NoFoundError
from ssguan.ignitor.vfs.error import FileSizeError, FileExistingError
from ssguan.ignitor.vfs.fs import BaseFS
from ssguan.ignitor.utility import kind


class LocalFS(BaseFS):
    
    FI_ROOTPATH = 'rootpath'
            
    def __init__(self, fsinfo):
        BaseFS.__init__(self, fsinfo)
        if self.FI_ROOTPATH not in fsinfo.kwargs:
            raise NoFoundError('configure item', self.FI_ROOTPATH)
              
    @property
    def rootpath(self):
        return self._fsinfo.kwargs[self.FI_ROOTPATH]
        
    def save_file(self, filepath, content):        
        if len(content) > self._fsinfo.maxsize * 1024 * 1024:
            raise FileSizeError(filepath, self._fsinfo.maxsize)
        if self.has_file(filepath) and not self._fsinfo.overwrite:
            raise FileExistingError(self._fsinfo.fs_name, filepath)
        filepath = self.__filepath(filepath)
        filepaths = filepath.rsplit(os.sep)
        if len(filepaths) > 1:
            fp = filepaths[0]
            for i in range(1, len(filepaths) - 1):
                fp += os.sep + filepaths[i]
                if not os.path.exists(fp):
                    os.mkdir(fp)
        with open(filepath, 'wb') as fileobj:
            content = kind.unibytes(content)
            fileobj.write(content)
        return True
    
    def get_file(self, filepath):
        if not self.has_file(filepath):
            raise NoFoundError(self._fsinfo.fs_name, filepath)
        filepath = self.__filepath(filepath)
        with open(filepath, 'rb') as fileobj:
            content = fileobj.read()
            fileobj.close()
        return content
    
    def delete_file(self, filepath):
        if not self.has_file(filepath):
            raise NoFoundError(self._fsinfo.fs_name, filepath)
        filepath = self.__filepath(filepath)
        os.remove(filepath)
        return True
    
    def has_file(self, filepath):        
        filepath = self.__filepath(filepath)
        return os.path.exists(filepath)
    
    def __filepath(self, filepath):
        filepath = "%s/%s" % (self.rootpath, filepath) 
        filepath = filepath.replace('\\', os.sep)
        filepath = filepath.replace('\\\\', os.sep)
        filepath = filepath.replace('/', os.sep)
        filepath = filepath.replace('//', os.sep)
        return filepath
    
    