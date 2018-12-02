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

from ssguan.ignitor.base.error import NoFoundError, NoSupportError
from ssguan.ignitor.utility import parallel
from ssguan.ignitor.vfs import config as fs_config
from ssguan.ignitor.vfs.lofs import LocalFS


__fses = {}
__lock = parallel.create_lock()

def extract_vfspath(vfs_path):
    """
        Return (fs_name, filepath)
    """
    f = vfs_path.split("://")
    return (f[0], f[1])

def build_vfspath(fs_name, filepath):
    return "%s://%s" % (fs_name, filepath)

def save_file(filepath, content, fs_name=None):
    """
        Save content to filepath.
    """     
    fs = get_fs(fs_name)
    fs.save_file(filepath, content)
    return build_vfspath(fs_name, filepath)
    
def read_file(vfs_path):
    """
        Read content from vfs_path.
        :param vfs_path: vfs path eg. default://ff/aa/c.csv
    """    
    (fs_name, filepath) = extract_vfspath(vfs_path)
    fs = get_fs(fs_name)
    return fs.read_file(filepath)

def delete_file(vfs_path):
    """
        Delete file with the vfs_path.
        :param vfs_path: vfs path eg. default://ff/aa/c.csv
    """    
    (fs_name, filepath) = extract_vfspath(vfs_path)
    fs = get_fs(fs_name)
    return fs.delete_file(filepath)

def has_file(vfs_path):
    """
        Check if the file with the vfs_path exists.
        :param vfs_path: vfs path eg. default://ff/aa/c.csv
    """    
    (fs_name, filepath) = extract_vfspath(vfs_path)
    fs = get_fs(fs_name)
    return fs.delete_file(filepath)

def get_fs(fs_name=None):
    """
        Return file system.
    """
    fsinfo = fs_config.get_default_fsinfo() if fs_name is None else fs_config.get_fsinfo(fs_name)
    if fsinfo is None:
        raise NoFoundError("FS", fs_name)
    if fs_name in __fses:
        return __fses[fs_name]
    else:        
        try:
            __lock.acquire()
            __fses[fs_name] = __new_fs(fsinfo)
        finally:
            __lock.release()
        return __fses[fs_name]

def __new_fs(fsinfo):
    if fsinfo.is_lofs():
        return LocalFS(fsinfo)
    raise NoSupportError("FS Type", fsinfo.fs_type)
