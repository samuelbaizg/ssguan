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
import shutil
import zipfile

import ConfigParser as configparser


def zip_dir(dir_path, zipfile_path):
    filelist = []
    if os.path.isfile(dir_path):
        filelist.append(dir_path)
    else :
        for root, dirs, files in os.walk(dir_path):
            for name in files:
                filelist.append(os.path.join(root, name))
        
    zf = zipfile.ZipFile(zipfile_path, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dir_path):]
        zf.write(tar, arcname)
    zf.close()

def unzip_file(zipfile_path, savedir_path):
    if not os.path.exists(savedir_path):
        os.makedirs(savedir_path)
    zfile = zipfile.ZipFile(zipfile_path)
    for name in zfile.namelist():
        if name.endswith("/"):
            dirname = savedir_path + os.sep + name
            if os.path.exists(dirname):
                os.removedirs(dirname)
            os.makedirs(dirname)
        else:
            filename = savedir_path + os.sep + name
            if os.path.exists(filename):
                os.remove(filename)
            fd = open(filename, 'wb')
            fd.write(zfile.read(name))
            fd.close()
    zfile.close()
    
# copy all the files/directories under srcpath to despath
def copy_tree(srcpath, despath):
    if not os.path.exists(despath):
        os.makedirs(despath)
    srcfilenames = os.listdir(srcpath)
    for srcfilename in srcfilenames:
        srcfilepath = srcpath + os.sep + srcfilename
        if os.path.isdir(srcfilepath):
            shutil.copytree(srcfilepath, despath + os.sep + srcfilename)
        else:
            shutil.copy(srcfilepath, despath)

def delete_files(dir_path, extension):
    dir_list = os.listdir(dir_path)
    for entry in dir_list:
        entry_fp = dir_path + os.sep + entry
        if os.path.isdir(entry_fp) == True:
            delete_files(entry_fp, extension)
        elif entry_fp.endswith(extension):
            os.remove(entry_fp)
            
def safewrite(filename, content):
    """Writes the content to a temp file and then moves the temp file to 
    given filename to avoid overwriting the existing file in case of errors.
    """
    f = file(filename + '.tmp', 'w')
    f.write(content)
    f.close()
    os.rename(f.name, filename)
    
def get_configparser(filepath, defaults=None):
    cp = configparser.ConfigParser(defaults)
    if hasattr(filepath, 'readline'):
        cp.readfp(filepath)
    else:
        if not os.path.exists(filepath):
            return None
        cp.read(filepath)
    return cp