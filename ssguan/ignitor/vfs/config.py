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
#  limitations under the Liense.

from ssguan.ignitor.base.struct import Storage
from ssguan.ignitor.utility import  io


__SECTION_FSES = "fses"
__OPTION_FSKEYS = 'keys'
__SECTION_FS_DEFAULT = "default"

__fsinfos = Storage()

def file_config(filepath, defaults=None):
    parser = io.get_configparser(filepath, defaults=defaults)
    global __cacheinfos
    keys = parser.get(__SECTION_FSES, __OPTION_FSKEYS)
    keys = keys.split(",")
    for key in keys:
        __fsinfos[key] = __parse_fsinfo(parser, key)

def get_default_fsinfo():
    """
        Return default FsInfo
    """
    return __fsinfos[__SECTION_FS_DEFAULT]

def get_fsinfo(fs_name):
    """
        Return FSInfo
        :param fs_name|str:
    """
    return __fsinfos[fs_name]


def __parse_fsinfo(parser, fs_name):
    fs_section = "fs_%s" % fs_name 
    maxsize = parser.get(fs_section, FSInfo.FI_MAXSIZE)
    overwrite = parser.get(fs_section, FSInfo.FI_OVERWRITE)
    fstype = parser.get(fs_section, FSInfo.FI_FS_TYPE)
    others = {}
    for (key, value) in parser.items(fs_section):
        if key not in (FSInfo.FI_MAXSIZE, FSInfo.FI_OVERWRITE, FSInfo.FI_FS_TYPE):
            others[key] = value
    return FSInfo(fs_name, fstype, maxsize, overwrite, **others)

class FSInfo(object):
    
    FI_MAXSIZE = "maxsize"
    FI_OVERWRITE = "overwrite"
    FI_FS_TYPE = "fs_type"
    def __init__(self, fs_name, fs_type, maxsize, overwrite, **kwargs):        
        self.__fs_name = fs_name
        self.__fs_type = fs_type
        self.__maxsize = maxsize
        self.__overwrite = overwrite
        self.__kwargs = kwargs
        
    @property
    def fs_name(self):
        return self.__fs_name
    
    @property
    def maxsize(self):
        """
            The unit is megabytes
        """
        return float(self.__maxsize)
    
    @property
    def overwrite(self):
        return True if self.__overwrite.lower() in ('yes','true') else False
    
    def is_lofs(self):
        """
            File system in local directory.
        """
        return self.__fs_type == 'local'
    
    @property
    def kwargs(self):
        return self.__kwargs
