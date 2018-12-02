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
from core.model import Tag, TagModel


def add_tag(tag_name, model_name, tag_order, user_id, modifier_id):
    tag = Tag()                    
    tag.tag_name = tag_name
    tag.model_name = model_name
    tag.tag_order = tag_order
    tag.creator_id = user_id
    tag.put(modifier_id)
    return tag

def update_tag(tag_id, tag_name, model_name, tag_order, user_id, modifier_id):
    tag = Tag.get_by_key(tag_id)
    tag.tag_name = tag_name
    tag.model_name = model_name
    tag.tag_order = tag_order
    tag.creator_id = user_id
    tag.put(modifier_id)
    return tag
    

def get_tag(tag_name, model_name, user_id):
    query = Tag.all()
    query.filter("tag_name =", tag_name)
    query.filter("model_name =", model_name)
    query.filter("creator_id =", user_id)
    count = query.count()
    if count > 0:
        return query.get()
    else:
        return None

def fetch_tags(user_id, model_name):
    query = Tag.all("a")
    query.filter("creator_id =", user_id)
    query.filter("model_name =", model_name)
    
    query.order("a.tag_order")
    tags = query.fetch()
    for tag in tags:
        tag.modelcount = get_tag_modelcount(tag.uid, model_name)
    return tags
        

def delete_tag(tag_id, modifier_id):
    tag = Tag.get_by_key(tag_id)
    delete_tagmodels(modifier_id, tag_id, tag.model_name)
    return tag.delete(modifier_id)

def add_tagmodel(model_name, model_key, tag_id, modifier_id):
    query = TagModel.all()
    query.filter("tag_id =", tag_id)
    query.filter("model_key =", model_key)
    query.filter("model_name =", model_name)
    if query.count() == 0:
        tagmodel = TagModel()
        tagmodel.model_name = model_name
        tagmodel.model_key = str(model_key)
        tagmodel.tag_id = tag_id
        tagmodel.put(modifier_id)
    else:
        tagmodel = query.get()
    return tagmodel

def get_tag_modelcount(tag_id, model_name):
    query = TagModel.all("a")
    query.filter("a.tag_id =", tag_id)
    query.filter("a.model_name =", model_name)
    return query.count()

def delete_tagmodels(tag_id=None, model_nk=None, modifier_id=None):
    query = TagModel.all()
    if tag_id != None:
        query.filter("tag_id =", tag_id)
    if model_nk != None:
        query.filter("model_name =", model_nk[0])
        query.filter("model_key =", str(model_nk[1]))
    return query.delete(modifier_id)

