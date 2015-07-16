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

import conf
from core import sysprop, ioutil
from core.error import CoreError
from error import FileSizeExceededError
from model import Filex

def _save_file(content, rootpath, savepath):
    filepath = "%s/%s" % (rootpath, savepath) 
    filepath = filepath.replace('\\', os.sep)
    filepath = filepath.replace('\\\\', os.sep)
    filepath = filepath.replace('/', os.sep)
    filepath = filepath.replace('//', os.sep)
    filepaths = filepath.rsplit(os.sep)
    if len(filepaths) > 1:
        fp = filepaths[0]
        for i in range(1, len(filepaths) - 1):
            fp += os.sep + filepaths[i]
            if not os.path.exists(fp):
                os.mkdir(fp)
            elif not os.path.isdir(fp):
                raise CoreError("fp %s is not a directory" , fp)
    fileobj = open(filepath, 'wb')
    fileobj.write(content)
    fileobj.close()
    return filepath

def _get_file(rootpath, savepath):
    filepath = "%s/%s" % (rootpath, savepath) 
    filepath = filepath.replace('\\', os.sep)
    filepath = filepath.replace('\\\\', os.sep)
    filepath = filepath.replace('/', os.sep)
    filepath = filepath.replace('//', os.sep)
    fileobj = open(filepath, 'rb')
    content = fileobj.read()
    fileobj.close()
    return content

def _delete_file(rootpath, savepath):
    filepath = "%s/%s" % (rootpath, savepath) 
    filepath = filepath.replace('\\', os.sep)
    filepath = filepath.replace('\\\\', os.sep)
    filepath = filepath.replace('/', os.sep)
    filepath = filepath.replace('//', os.sep)
    os.remove(filepath)

def create_file(file_name, file_content, model_name, model_key, user_id, modifier_id):
    max_size = conf.get_upload_file_maximum_size(user_id)
    if len(file_content) > max_size:
        raise FileSizeExceededError(max_size / 1024 / 1024)
    filex = Filex()
    filex.file_name = file_name
    if "." in filex.file_name:            
        filex.file_type = filex.file_name.rsplit(".")[1]
    else:
        filex.file_type = ""
    filex.creator_id = user_id
    filex.model_name = model_name
    filex.model_key = model_key
    file_name = str(user_id) + "_" + str(model_name) + "_" + str(model_key) + "_" + file_name
    filex.save_path = os.sep + model_name + os.sep + file_name
    filex.root_path = os.sep + str(user_id) + os.sep + sysprop.get_sysprop_value("UPLOADFILE_ROOTPATH", default=conf.DEFAULT_UPLOADFILE_ROOTPATH)
    filex.file_size = len(file_content)
    filex.file_hash = ioutil.get_file_md5(file_content)
    _save_file(file_content, filex.root_path, filex.save_path)
    filex.put(modifier_id)
    return filex
    
def delete_file(file_id, modifier_id):
    filex = Filex.get_by_key(file_id)
    _delete_file(filex.root_path, filex.save_path)
    filex.delete(modifier_id)
    return True

def get_file(file_id, content=False):
    filex = Filex.get_by_key(file_id)
    if content is True:
        filex.file_content = _get_file(filex.root_path, filex.save_path)
    return filex 

def delete_files(user_id, model_nk=None, modifier_id=None):
    query = Filex.all()
    query.filter("creator_id =", user_id)
    if model_nk != None:
        query.filter("model_name =", model_nk[0])
        query.filter("model_key =", str(model_nk[1]))
    files = query.fetch()
    for filex in files:
        _delete_file(filex.root_path, filex.save_path)
    result = query.delete(modifier_id)
    return result

def fetch_files(user_id, model_nk=None):
    query = Filex.all()
    query.what("uid", alias="file_id")
    query.what("creator_id", alias="creator_id")
    query.what("file_name", alias="file_name")
    query.filter("creator_id =", user_id)
    if model_nk is not None:
        query.filter("model_name =", model_nk[0])
        query.filter("model_key =", str(model_nk[1]))
        
    return query.fetch()
