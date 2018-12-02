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

from datetime import datetime
import imp
import os

import six

from ssguan import  config
from ssguan.commons import database, webb, dao, typeutils
from ssguan.commons import loggingg
from ssguan.commons.dao import Model, UniqueValidator
from ssguan.commons.error import Error
from ssguan.modules import  schedule, sysprop, auth, mqueue, entity


_logger = loggingg.get_logger(config.MODULE_UPDATE)

class Migration(Model):
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_UPDATE
    
    ver_id = dao.IntegerProperty("versionId", length=4, required=True, validator=UniqueValidator("ver_id"))
    upgraded = dao.BooleanProperty("upgraded", default=False)
    migrated_time = dao.DateTimeProperty("migratedTime", auto_utcnow=True)
    
    @classmethod
    def get_by_ver_id(cls, ver_id, dbconn=None):
        query = Migration.all(dbconn=dbconn)
        query = query.filter("ver_id =", int(ver_id))
        if query.count() == 0:
            mig = Migration()
            mig.ver_id = int(ver_id)
            mig.upgraded = False
            mig.create(Model.NULL_USER_ID)
        else:
            mig = query.get()
        return mig
        

def install():
        
    installfile = os.path.join(os.path.dirname(__file__) , "..", ".ssguan")
    if os.path.exists(installfile):
        _logger.error("ssguan was installed.")
        return False
    with open(installfile, "w") as file1:
        database.create_db(config.dbCFG.get_root_dbinfo())
        sysprop.install_module()
        auth.install_module()
        webb.install_module()
        entity.install_module()
        loggingg.install_module()
        mqueue.install_module()
        schedule.install_module()
        config.dbCFG.add_model_dbkey("%s_*" % config.MODULE_UPDATE, config.dbCFG.ROOT_DBKEY)
        Migration.create_schema()
        dbinfos = config.dbCFG.fetch_dbinfos()
        for dbinfo in dbinfos:
            database.create_db(dbinfo)
        file1.write("ssguan is installed on %s.\n" % typeutils.datetime_to_str(typeutils.utcnow(), "%Y-%m-%d %H:%M:%S.%f UTC"))
        file1.write("NO DELETE this file.")
        
def upgrade():
    ver_ids = _fetch_versions()
    for ver_id in ver_ids:
        migration = Migration.get_by_ver_id(ver_id)
        if not migration.upgraded:
            version = _get_version_instance(ver_id)
            try:
                version.upgrade()
                migration.upgraded = True
                migration.migrated_time = datetime.utcnow()
                migration.update(Model.NULL_USER_ID)
            except BaseException, e:
                _logger.fatal(e.message, exc_info=1)
                version.downgrade()
                raise e

def downgrade(ver_id):
    ver_id = int(ver_id)
    ver_ids = _fetch_versions()
    instance = None
    migration = None
    for verid in ver_ids:
        if verid > ver_id:
            migration = Migration.get_by_ver_id(verid)
            if migration.upgraded:
                raise UpdateError("The higher version %d is migrated, please downgrade the higher version first." , verid)
        elif verid == ver_id:
            migration = Migration.get_by_ver_id(verid)
            if migration.upgraded is False:
                raise UpdateError("This version %d is not migrated, please upgraded it first." , verid)
            else:
                instance = _get_version_instance(verid)
    if instance is not None:
        migration.upgraded = False
        migration.update()
        instance.downgrade()

def _fetch_versions():
    """
    Return all version ids in directory "versions"
    """
    versionpath = os.path.join(os.path.dirname(__file__) , "..", "versions")
    ver_ids = []
    for f in os.listdir(versionpath):
        if os.path.isfile(os.path.join(versionpath, f)) and f.endswith(".pya"):
            ver_id = os.path.basename(f).replace(".pya", "").replace("v", "")
            ver_ids.append(ver_id)
    ver_ids = sorted(ver_ids)
    return ver_ids

def _get_version_instance(ver_id):
    vername = "v%s" % ver_id
    verpath = os.path.join(os.path.dirname(__file__) , "..", "versions", "%s.pya" % vername)
    if not os.path.exists(verpath):
        raise UpdateError("%s does not exist.", verpath)
    verfile = open(verpath, "r")    
    vercode = "".join(verfile.readlines())
    verfile.close()
    vercode = compile(vercode, '<%s>' % vername, 'exec')
    mod = imp.new_module(vername)
    mod.__file__ = '<%s>' % verpath
    mod.__loader__ = __name__
    mod.__package__ = 'ssguan.commons.update'
    six.exec_(vercode, mod.__dict__)
    clazz = mod.__dict__.get('%s' % vername.upper())
    return clazz()

class UpdateError(Error):
    """
        UpdateError is to define the error for update.
    """
    def __init__(self, message, *args):
        super(UpdateError, self).__init__(message, *args)
    
    @property
    def code(self):
        return 1006
    
class Version(object):
    
    def __init__(self):    
        self._logger = loggingg.get_logger(config.MODULE_UPDATE)
    
    def upgrade(self):
        self._logger.info("Upgrading to %s", self.__class__.__name__)
        self._upgrade()
        self._logger.info("end upgrade %s", self.__class__.__name__)
    
    def downgrade(self):
        self._logger.info("Downgrading to %s", self.__class__.__name__)
        self._downgrade()
        self._logger.info("end downgrade %s", self.__class__.__name__) 
    
    def _upgrade(self):
        """To be override in sub class"""
        raise NotImplementedError("Version._upgrade")
    
    def _downgrade(self):
        """To be override in sub class"""
        raise NotImplementedError("Version._downgrade")
