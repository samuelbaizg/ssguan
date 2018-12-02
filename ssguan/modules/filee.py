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

from ssguan import config
from ssguan.commons import typeutils, dao, security
from ssguan.commons.dao import Model, RequiredError, Query
from ssguan.commons.error import Error, NoFoundError
from ssguan.modules import auth
from ssguan.modules.auth import RoleOperation, UnauthorizedError


class FileSizeError(Error):
    def __init__(self, filepath, filesize):
        super(FileSizeError, self).__init__("The filesize of {{filepath}} exceed {{filesize}} M, can't upload.", filepath=filepath, filesize=filesize)

    @property
    def code(self):
        return 1071      
    
class FileExistsError(Error):
    def __init__(self, fskey, filepath):
        super(FileExistsError, self).__init__("{{filepath}} existed in {{fskey}}.", filepath=filepath, fskey=fskey)
    
    @property
    def code(self):
        return 1072

class Filex(Model):
    @classmethod
    def meta_domain(cls):
        return config.MODULE_FILEE
    
    filename = dao.StringProperty("fileName", required=True, length=255, validator=[dao.IllegalValidator(), dao.UniqueValidator("filename")])
    filesize = dao.IntegerProperty("fileSize", required=True)
    filehash = dao.StringProperty("fileHash", required=True, length=80)
    fspath = dao.StringProperty("fsPath", required=True, length=80)
    
    def extract_fspath(self):
        """
            Return (fskey, filepath)
        """
        f = self.fspath.split("://")
        return (f[0], f[1] + "/" + self.filename)
    
    @classmethod
    def gen_fspath(cls, fskey, fielpath):
        return "%s://%s" % (fskey, fielpath)
    
def create_file(filepath, file_content, created_by):
    if not auth.has_permission(created_by, Filex, RoleOperation.OPERATION_CREATE):
        raise UnauthorizedError(RoleOperation.OPERATION_CREATE, Filex.get_modelname(), "")
    filex = Filex()
    filex.filename = os.path.basename(filepath)
    filex.filesize = len(file_content)
    filex.filehash = security.str_to_md5_hex(file_content)
    fs = get_fs(created_by)
    filex.fspath = Filex.gen_fspath(fs.fskey, os.path.dirname(filepath))
    fs.save_file(filepath, file_content)
    filex.create(created_by)
    return filex
    
def delete_file(file_id, deleted_by):
    if typeutils.str_is_empty(file_id):
        raise RequiredError("model key is required.- %s" % Filex.get_modelname())
    if not auth.has_permission(deleted_by, Filex, RoleOperation.OPERATION_DELETE):
        raise UnauthorizedError(RoleOperation.OPERATION_DELETE, Filex.get_modelname(), file_id)
    filex = Filex.get_by_key(file_id)
    if filex is None:
        raise NoFoundError(Filex, file_id)
    (fskey, filepath) = filex.extract_fspath()
    fs = get_fs(fskey)
    fs.delete_file(filepath)
    filex.delete(deleted_by)
    return True

def has_file(file_id, read_by):
    if typeutils.str_is_empty(file_id):
        raise RequiredError("model key is required.- %s" % Filex.get_modelname())
    if not auth.has_permission(read_by, Filex, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, Filex.get_modelname(), file_id)
    filex = Filex.get_by_key(file_id)
    return False if filex is None else True

def get_file(file_id, read_by, content=False):
    if typeutils.str_is_empty(file_id):
        raise RequiredError("model key is required.- %s" % Filex.get_modelname())
    if not auth.has_permission(read_by, Filex, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, Filex.get_modelname(), file_id)
    filex = Filex.get_by_key(file_id)
    if filex is None:
        raise NoFoundError(Filex, file_id)
    if content is True:
        (fskey, filepath) = filex.extract_fspath()
        fs = get_fs(fskey)
        filex.file_content = fs.get_file(filepath)
    return filex

def fetch_files(read_by, filename=None, rivars={}, limit=Query.DEFAULT_FETCH_LIMIT, offset=0, paging=False, mocallback=None):
    query = auth.gen_query_of_allowed_resources(read_by, Filex, RoleOperation.OPERATION_READ, **rivars)
    if query is None:
        return [] if paging is False else typeutils.gen_empty_pager()
    else:
        filters = []
        if filename is not None:
            filters.append({"property_op":"filename like", "value":"%" + filename + "%"})
        query.filter_x(filters, logic="and")
        return query.fetch(limit=limit, offset=offset, paging=paging, mocallback=mocallback)

class LocalFS(object):
    
    def __init__(self, fskey, rootpath, maxsize=4 * 1024 * 1024 * 1024, overwrite=False):
        """
        :param maxsize|float: unit is megabytes
        :param overwrite|Bool: True means overwrite the existed file with the same path, or else no.
        """
        self._fskey = fskey
        self._rootpath = rootpath
        self._maxsize = maxsize
        self._overwrite = overwrite
    
    @property
    def fskey(self):
        return self._fskey
            
    @property
    def rootpath(self):
        return self._rootpath
    
    @property
    def maxsize(self):
        return self._maxsize
    
    @property
    def overwrite(self):
        return self._overwrite
    
    def save_file(self, filepath, content):        
        if len(content) > self.maxsize * 1024 * 1024:
            raise FileSizeError(filepath, self.maxsize)
        if self.has_file(filepath) and not self.overwrite:
            raise FileExistsError(self.fskey, filepath)
        filepath = self.__filepath(filepath)
        filepaths = filepath.rsplit(os.sep)
        if len(filepaths) > 1:
            fp = filepaths[0]
            for i in range(1, len(filepaths) - 1):
                fp += os.sep + filepaths[i]
                if not os.path.exists(fp):
                    os.mkdir(fp)
        fileobj = open(filepath, 'wb')
        fileobj.write(content)
        fileobj.close()
        return True
    
    def get_file(self, filepath):
        if not self.has_file(filepath):
            raise NoFoundError(self.fskey, filepath)
        filepath = self.__filepath(filepath)
        fileobj = open(filepath, 'rb')
        content = fileobj.read()
        fileobj.close()
        return content
    
    def delete_file(self, filepath):
        if not self.has_file(filepath):
            raise NoFoundError(self.fskey, filepath)
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

def get_fs(fskey):
    fscfg = config.fileeCFG.get_fsinfo(fskey)    
    rootpath = fscfg[config.fileeCFG.FS_ROOTPATH]
    del fscfg[config.fileeCFG.FS_ROOTPATH]
    localfs = LocalFS(fskey, rootpath, **fscfg)
    return localfs

def get_default_fs():
    return get_fs(config.fileeCFG.DEFAULT_FSKEY)

def install_module():
    Filex.create_schema()
    config.dbCFG.add_model_dbkey("%s_*" % config.MODULE_FILEE, config.dbCFG.ROOT_DBKEY)
    config.fileeCFG.add_fsinfo(config.fileeCFG.DEFAULT_FSKEY, "c:", config.ID_SYSTEM)
    return True

def uninstall_module():
    Filex.delete_schema()
    config.dbCFG.delete_model_dbkey("%s_*" % config.MODULE_FILEE)
    config.fileeCFG.delete_fsinfo(config.fileeCFG.DEFAULT_FSKEY)
    return True
