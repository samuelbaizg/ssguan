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

from ssguan.ignitor.base.error import NoFoundError, InvalidError
from ssguan.ignitor.utility import kind, io, reflect
from ssguan.ignitor.base import struct


__setting = None

__conduits = struct.Storage()
__processors = struct.Storage()

__SECTION_SETTING = "setting"

__SECTION_CONDUIT = "conduit"
__SECTION_PROCESSOR = "processor"

class Setting:
    
    ASYN_SCAN_DIR = 'scan_dir'
    ASYN_SCAN_FILENAME = 'scan_filename'
    
    def __init__(self, **kwargs):
        self.__scan_dir = kwargs[self.ASYN_SCAN_DIR]
        self.__scan_filename = kwargs[self.ASYN_SCAN_FILENAME]
        if not os.path.isabs(self.__scan_dir):
            self.__scan_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', self.__scan_dir)
        else:    
            if not os.path.exists(self.__scan_dir):
                self.__scan_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..')
    
    @property
    def scan_dir(self):
        return self.__scan_dir
    
    @property
    def scan_filename(self):
        return self.__scan_filename

def get_setting():
    return __setting

def file_config(filepath, defaults=None):
    global __setting, __condicts, __processors
    parser = io.get_configparser(filepath, defaults=defaults)
    __setting = Setting(**__parse_setting(parser))
    (conduits, processors) = __parse_async_configs(__setting)
    __conduits.update(**conduits)
    __processors.update(**processors)
    
def __parse_async_configs(setting):
    conduits = {}
    processors = {}
    def parse_conduit(conduitcfg):
        for key, value in conduitcfg.items():
            if key in conduits:
                raise InvalidError("conduit %s" % key, " it has been configured.")
            else:
                vo = struct.Storage()
                for k, v in value.items():
                    vo[k] = v
                vo.clazz = reflect.import_module(vo['clazz'])
                if vo.clazz is None:
                    raise NoFoundError("Conduit" , value['clazz'])
                else:
                    vo.instance = vo.clazz(key, **vo.arguments)                 
                conduits[key] = vo
    def parse_processor(processorcfg):
        for key, value in processorcfg.items():
            if key in processors:
                raise InvalidError("Processor %s" % key, " it has been configured.")
            else:
                vo = struct.Storage()
                for k, v in value.items():
                    vo[k] = v
                vo.clazz = reflect.import_module(vo['clazz'])
                if vo.clazz is None:
                    raise NoFoundError("Processor" , value['clazz'])
                condict_name = vo['conduit_name']
                if  condict_name not in conduits:
                    raise NoFoundError("Conduit with the name" , condict_name)
                else:
                    conduit = conduits[condict_name]
                    vo.conduit = conduit.instance                 
                processors[key] = vo
    filepaths = io.discover_files(setting.scan_dir, setting.scan_filename)
    jsons = []
    for fp in filepaths:
        jsonstr = io.read_file(fp) 
        json = kind.json_to_object(jsonstr)
        jsons.append(json)
    for json in jsons:
        conduitcfg = json[__SECTION_CONDUIT]
        processorcfg = json[__SECTION_PROCESSOR]
        parse_conduit(conduitcfg)
        parse_processor(processorcfg)
    return (conduits, processors)

def __parse_setting(parser): 
    cfg = {}
    for (key, value) in parser.items(__SECTION_SETTING):
        cfg[key] = value
    return cfg
    
      
def get_processor(message_type):
    """
        Return message processor
        :param message_type|str:
    """
    global __processors
    return __processors[message_type]

def get_conduit(message_type):
    """
        Return message conduit instance
        :param message_type|str:
    """
    global __processors
    return __processors[message_type].conduit
