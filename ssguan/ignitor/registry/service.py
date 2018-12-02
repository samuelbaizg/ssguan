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

from ssguan.ignitor.base import context
from ssguan.ignitor.base.error import NoFoundError
from ssguan.ignitor.registry.model import Registry
from ssguan.ignitor.utility import kind
from ssguan.ignitor.base.error import RequiredError


def get_item(item_key):
    """
        Get the item.
    """
    if kind.str_is_empty(item_key):
        raise RequiredError("item_key")
    query = Registry.all()
    query.filter("item_key =", item_key)
    return query.get()

def get_item_value(item_key):
    """
        Get the item value.
        :param item_key|str: the item key
        :rtype object:
    """
    if kind.str_is_empty(item_key):
        raise RequiredError("item_key")
    query = Registry.all()
    query.filter("item_key =", item_key)
    registry = query.get()   
    value = registry.item_value if registry != None else None        
    return value

def has_item(item_key, valid_flag=None):
    """
        Check if the item exists.
    """
    query = Registry.all()
    query.filter("item_key =", item_key)
    if valid_flag is not None:
        query.filter("valid_flag =", valid_flag)
    return query.count() > 0

def fetch_items(parent_key, valid_flag=None):
    """
        Fetch the items by parent_key
        :param parent_key|str:
        :rtype list of Registry:
    """
    query = Registry.all()
    if parent_key is not None:        
        query.filter("parent_key =", parent_key)
    if valid_flag is not None:
        query.filter("valid_flag =", valid_flag)
    return query.fetch()

def create_item(item_key, item_value, item_desc, parent_key=Registry.ROOT_KEY, valid_flag=True):
    """
        Create an item.
    """
    if kind.str_is_empty(item_key):
        raise RequiredError("item_key")
    if item_value is None:
        raise RequiredError("item_value")
    registry = Registry(item_key=item_key, item_value=item_value, item_desc=item_desc, parent_key=parent_key, valid_flag=valid_flag)
    registry.create(context.get_user_id())
    return registry

def update_item(item_key, item_value, item_desc, parent_key, valid_flag):
    """
        Update item.
    """
    if kind.str_is_empty(item_key):
        raise RequiredError("item_key")
    if item_value is None:
        raise RequiredError("item_value")
    item = get_item(item_key)
    if item is None:
        raise NoFoundError("item", item_key)    
    query = Registry.all()
    query.filter("item_key =", item_key)
    query.set("item_value", item_value)
    query.set("item_desc", item_desc)
    query.set("parent_key", parent_key)
    query.set("valid_flag", valid_flag)
    return query.update(context.get_user_id())

def invalid_item(item_key, valid_flag=False):
    """
        Update item valid_flag.
    """
    if kind.str_is_empty(item_key):
        raise RequiredError("item_key")
    query = Registry.all()
    query.filter("item_key =", item_key)
    query.set("valid_flag", valid_flag)    
    return query.update(context.get_user_id())

def delete_item(item_key):
    """
        Delete item.
    """
    if kind.str_is_empty(item_key):
        raise RequiredError("item_key")
    query = Registry.all()
    query.filter("item_key =", item_key)
    return query.delete(context.get_user_id())

