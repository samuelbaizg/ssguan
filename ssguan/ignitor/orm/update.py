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


import imp
import os

import six

from ssguan.ignitor import IGNITOR_DOMAIN
from ssguan.ignitor.orm import properti, dbpool, config as orm_config
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.orm.validator import UniqueValidator
from ssguan.ignitor.utility import io, kind


SCAN_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..')
SCAN_FILENAME = 'patch.pya'

class Patch(Model):
    
    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN
    
    module_name = properti.StringProperty(length=80, required=True)
    version_id = properti.IntegerProperty(length=4, required=True, validator=UniqueValidator("version_id", scope=["module_name"]))
    upgraded = properti.BooleanProperty(default=False)
    upgrade_time = properti.DateTimeProperty() 
    
    @classmethod
    def get_by_ver_id(cls, module_name, version_id, dbconn=None):
        query = Patch.all()
        query = query.filter("module_name =", module_name)
        query = query.filter("version_id =", int(version_id))
        if query.count() == 0:
            mig = Patch()
            mig.module_name = module_name
            mig.version_id = int(version_id)
            mig.upgrade_flag = False
            mig.create(Model.NULL_USER_ID)
        else:
            mig = query.get()
        return mig

def install():
    if not dbpool.has_db(orm_config.get_default_dbinfo()):
        dbpool.create_db(orm_config.get_default_dbinfo())
    if not Patch.has_schema():
        Patch.create_schema()
    
def upgrade(module_name=None):
    patches = __load_patches()
    for (mod_name, ver_id, patch_inst) in patches:
        if (module_name is None or mod_name == module_name):
            for i in range(1, int(ver_id) + 1):
                patch = Patch.get_by_ver_id(mod_name, i)
                if not patch.upgraded:
                    try:
                        patch_inst.upgrade()
                        patch.upgraded = True
                        patch.upgrade_time = kind.utcnow()
                        patch.update(Model.NULL_USER_ID)
                    except BaseException as e:
                        patch_inst.downgrade()
                        raise e

def __load_patches():
    patches = []
    filepaths = io.discover_files(SCAN_DIR, SCAN_FILENAME)
    def get_patch(filepath):
        verfile = open(filepath, "r")    
        vercode = "".join(verfile.readlines())
        verfile.close()
        vercode = compile(vercode, '<%s>' % vercode, 'exec')
        mod = imp.new_module(fp)
        mod.__file__ = '<%s>' % fp
        mod.__loader__ = __name__
        mod.__package__ = 'ignitor.orm'
        six.exec_(vercode, mod.__dict__)
        mod_name = mod.__dict__.get('MOD_NAME')
        ver_id = mod.__dict__.get('VER_ID')       
        clazz = mod.__dict__.get('VER_%s' % ver_id)
        return (mod_name, ver_id , clazz())
    for fp in filepaths:
        (mod_name, ver_id, patch) = get_patch(fp)
        patches.append((mod_name, ver_id, patch))
    return patches
