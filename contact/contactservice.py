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
from contact.contactmodel import GroupVersion, GroupComponent, \
    GroupException, ContactLeave
from contactmodel import  Contact, ContactGroup, Group
from core import model, user, strutil, cache
from core.error import Error, CoreError
from core.model import Resolver
from core.service import Service
from task.taskmodel import Task


CACHESPACE_GROUPNAME = "groupname"
CACHESPACE_CONTACTNAME = "contactname"

class ContactService(Service):
    
    def create_group(self, group, modifier_id):
        query = Group.all()
        query.order("-group_order")
        if query.count() > 0:
            group.group_order = query.get().group_order + 1
        else:
            group.group_order = 1
        group.put(modifier_id)
    
    def update_group(self, group, modifier_id):
        group.put(modifier_id)
        return group
    
    def delete_group(self, group_id, modifier_id):
        group = Group.get_by_key(group_id)
        self.delete_contactgroups(modifier_id, group_id=group_id)
        self.delete_groupexceptions(group_id, modifier_id)
        self.delete_groupversions(group_id, modifier_id)
        self.delete_groupcomponents(group_id, modifier_id)
        group.delete(modifier_id)
        return True
    
    def get_group_name(self, group_id):
        if group_id == None or group_id == model.EMPTY_UID:
            return ""
        name = cache.get(CACHESPACE_GROUPNAME, group_id)
        if name != None:
            return name
        else:
            group = self.get_group(group_id)
            name = group.group_name if group is not None else ''
            cache.put(CACHESPACE_GROUPNAME, group_id, name)
            return name
    
    def get_group(self, group_id):
        return Group.get_by_key(group_id)
    
    def fetch_groups(self, user_id, is_shared=None, sharetome=None, withcontactcount=True):
        query = Group.all("a")
        if is_shared != None:
            query.filter("is_shared =", is_shared)
        if sharetome:
            query.model(ContactGroup.get_modelname(), alias="b", join="inner", on="a.uid=b.group_id")
            query.model(Contact.get_modelname(), alias="c", join="inner", on="c.uid=b.contact_id")
            query.filter("c.bind_user_id =", user_id)
            query.filter("a.is_shared =", True)
        else:
            query.filter("creator_id =", int(user_id))
        
        def group_proc(group):
            if withcontactcount:
                group.contactcount = self.get_contactcount(False, user_id, group_id=group.key())
            
        groups = query.fetch(model_proc=group_proc)
        return groups
    
    def create_groupversion(self, groupversion, modifier_id):
        groupversion.put(modifier_id)
        return groupversion
        
    def update_groupversion(self, groupversion, modifier_id):
        groupversion.put(modifier_id)
        return groupversion
        
    def delete_groupversion(self, version_id, modifier_id):
        groupversion = GroupVersion.get_by_key(version_id)
        groupversion.delete(modifier_id)
        from task.taskservice import TaskService
        TaskService.get_instance().delete_taskversions(modifier_id, version_id=version_id)
        return True
    
    def delete_groupversions(self, group_id, modifier_id):
        groupversions = self.fetch_groupversions(group_id)
        for gv in groupversions:
            self.delete_groupversion(gv.key(), modifier_id)
    
    def fetch_groupversions(self, group_id):
        query = GroupVersion.all()
        query.filter("group_id =", group_id)
        return query.fetch()
    
    def create_groupcomponent(self, groupcomponent, modifier_id):
        groupcomponent.put(modifier_id)
        return groupcomponent
        
    def update_groupcomponent(self, groupcomponent, modifier_id):
        groupcomponent.put(modifier_id)
        return groupcomponent
        
    def delete_groupcomponent(self, component_id, modifier_id):
        groupcomponent = GroupComponent.get_by_key(component_id)
        groupcomponent.delete(modifier_id)
        from task.taskservice import TaskService
        TaskService.get_instance().delete_taskcomponents(modifier_id, component_id=component_id)
        return True
    
    def delete_groupcomponents(self, group_id, modifier_id):
        groupcomponents = self.fetch_groupcomponents(group_id)
        for gc in groupcomponents:
            self.delete_groupcomponent(gc.key(), modifier_id)
        
    def fetch_groupcomponents(self, group_id):
        query = GroupComponent.all()
        query.filter("group_id =", group_id)
        return query.fetch()
    
    def create_groupexception(self, groupexception, modifier_id):
        groupexception.put(modifier_id)
        return groupexception
        
    def update_groupexception(self, groupexception, modifier_id):
        groupexception.put(modifier_id)
        return groupexception
        
    def delete_groupexception(self, exception_id, modifier_id):
        groupworkexception = GroupException.get_by_key(exception_id)
        groupworkexception.delete(modifier_id)
        return True
    
    def delete_groupexceptions(self, group_id, modifier_id):
        groupexceptions = self.fetch_groupexceptions(group_id)
        for ge in groupexceptions:
            self.delete_groupexception(ge.key(), modifier_id)
        
    def fetch_groupexceptions(self, group_id):
        query = GroupException.all()
        query.filter("group_id =", group_id)
        return query.fetch()
    
    def create_contact(self, contact, modifier_id):
        contact.is_trashed = False
        contact = self.link_contact_to_user(contact, contact.bind_user_account)
        contact.put(modifier_id)
        self.create_contactgroups(contact.key(), contact.group_ids, modifier_id)
        return contact
    
    def update_contact(self, contact, modifier_id):
        ct = Contact.get_by_key(contact.uid)
        if ct.is_trashed : 
            raise Error("cont_error_trashedupdate")
        if ct.creator_id != modifier_id:
            raise Error("cont_error_updatesharedcontact")
        contact = self.link_contact_to_user(contact, contact.bind_user_account)        
        contact.put(modifier_id)
        self.create_contactgroups(contact.key(), contact.group_ids, modifier_id)
        return contact
    
    def recover_contact(self, contact_id, modifier_id):
        ct = Contact.get_by_key(contact_id)
        ct.is_trashed = False
        ct.put(modifier_id)
        return ct
    
    def move_contact(self, contact_id, group_ids, modifier_id):
        self.delete_contactgroups(modifier_id, contact_id)
        if type(group_ids) == int:
            group_ids = [group_ids]
        for group_id in group_ids:
            cg = ContactGroup()
            cg.contact_id = contact_id
            cg.group_id = group_id
            cg.put(modifier_id)
        return cg
    
    def create_contactgroup(self, contactgroup, modifier_id):
        contactgroup.put(modifier_id)
        return contactgroup
    
    def update_contactgroup(self, contactgroup, modifier_id):
        contactgroup.put(modifier_id)
        return contactgroup
    
    def delete_contactgroup(self, resource_id, modifier_id):
        contactgroup = ContactGroup.get_by_key(resource_id)
        contactgroup.delete(modifier_id)
        return True
    
    def fetch_contactgroups(self, contact_id=None, group_id=None):
        if contact_id is None and group_id is None:
            raise CoreError("contact_id and group_id can't be None at the same time.")
        query = ContactGroup.all()
        if contact_id != None:
            query.filter("contact_id =", contact_id)
        if group_id != None:
            query.filter("group_id =", group_id)
        query.order("contact_id")
        cgs = query.fetch()
        return cgs
    
    def create_contactgroups(self, contact_id, group_ids, modifier_id):
        old_group_ids = map(lambda x: x.group_id, self.fetch_contactgroups(contact_id=contact_id))
        c_g_ids = set(group_ids).intersection(set(old_group_ids))
        add_gids = set(group_ids) - c_g_ids
        del_gids = set(old_group_ids) - c_g_ids
        
        for gid in add_gids:
            cg = ContactGroup(contact_id=contact_id, group_id=gid)
            self.create_contactgroup(cg, modifier_id)
        for gid in del_gids:
            self.delete_contactgroups(modifier_id, contact_id=contact_id, group_id=gid)
        
    def delete_contactgroups(self, modifier_id, contact_id=None, group_id=None):
        if contact_id is None and group_id is None:
            raise CoreError("the contact_id and group_id can't be None at the same time.")
        query = ContactGroup.all()
        if contact_id != None:
            query.filter("contact_id =", contact_id)
        if group_id != None:
            query.filter("group_id =", group_id)
        query.delete(modifier_id)
        return True
    
    def get_contact_name(self, contact_id):
        if contact_id == None or contact_id == model.EMPTY_UID:
            return ""
        name = cache.get(CACHESPACE_CONTACTNAME, contact_id)
        if name != None:
            return name
        else:
            contact = self.get_contact(contact_id)
            name = contact.contact_name if contact is not None else ''
            cache.put(CACHESPACE_CONTACTNAME, contact_id, name)
            return name
    
    def get_myself(self, user_id):
        query = Contact.all()
        query.filter("bind_user_id =", user_id)
        query.filter("creator_id =", user_id)
        if query.count() > 0:
            contact = query.get()
        else:
            contact = None
        return contact
    
    def get_contact(self, contact_id):
        contact = Contact.get_by_key(contact_id)
        return contact
    
    def trash_contacts(self, contact_ids, is_trashed, modifier_id):
        for contact_id in contact_ids:
            contact = Contact.get_by_key(contact_id)
            contact.is_trashed = is_trashed
            contact.put(modifier_id)
        return True
    
    def empty_trash(self, user_id, modifier_id):
        query = Contact.all()
        query.filter("is_trashed =", True)
        query.filter("creator_id =", user_id)
        status = query.delete(modifier_id)
        return status
    
    def delete_contact(self, contact_id, modifier_id):
        contact = Contact.get_by_key(int(contact_id))
        if contact.is_trashed:
            contact.delete(modifier_id)
            self.delete_contactgroups(modifier_id, contact_id=contact_id)
        else:
            if contact.creator_id != modifier_id:
                raise Error("cont_error_deletesharedcontact")
            
            query = Task.all()
            query.filter("assignee_id =", contact_id)
            query.filter("is_trashed =", False)
            if query.count() > 0:
                raise Error('cont_error_assignedtasks')
            else:
                self.trash_contacts([contact.uid], True, modifier_id)
        return True
    
    def fetch_contacts(self, user_id, filters=None, limit=20, offset=0):
        
        def append_filters(query):
            for ft in filters:
                for (key, value) in ft.items():
                    for nr in CONTACTRESOLVERS:
                        nrinst = nr(key, value)
                        query.extend(nrinst)
                        
        query = Contact.all(alias="a")
        for key in Contact.get_properties(persistent=True).keys():
            query.what("a.%s" % key, alias=key)
        query.select("DISTINCT")
        group_ids = self.fetch_my_groups(user_id, onlyrtnids=True)
        if len(group_ids) > 0:
            query.model(ContactGroup.get_modelname(), alias="b", join="left", on="a.uid = b.contact_id")
            query.filter("b.group_id in", group_ids, parenthesis="(")
            query.filter("a.creator_id =", user_id, logic="or", parenthesis=")")
        else:
            query.filter("a.creator_id =", user_id)
        query.order("-a.uid")
        
        if filters != None:
            append_filters(query)
        
        if not query.has_filter("a.is_trashed"):
            query = query.filter("a.is_trashed =", False)
            
        def contact_proc(contact):
            contact.contactLeaves = self.fetch_contactleaves(contact.key())          
        return query.fetch(limit, offset, paging=True, model_proc=contact_proc)
    
    def fetch_my_contacts(self, user_id):
        query = Contact.all(alias="a")
        query.select("DISTINCT")
        query.what("a.uid", alias="uid")
        query.what("a.contact_name", alias="contact_name")
        query.what("a.creator_id", alias="creator_id")
        group_ids = self.fetch_my_groups(user_id, onlyrtnids=True)
        if len(group_ids) > 0:
            query.model(ContactGroup.get_modelname(), alias="b", join="left", on="a.uid = b.contact_id")
            query.filter("b.group_id in", group_ids, parenthesis="(")
            query.filter("a.creator_id =", user_id, logic="or", parenthesis=")")
        else:
            query.filter("a.creator_id =", user_id)
        query.order("-a.uid")
        
        query = query.filter("a.is_trashed =", False)
        def contact_proc(contact):
            """"""
        return query.fetch(model_proc=contact_proc)
    
    def fetch_contacts_created_by(self, user_id):
        query = Contact.all()
        query.what("uid")
        query.what("creator_id")
        query.what("contact_name")
        query.filter("creator_id =", user_id)
        query.order("-uid")
        query = query.filter("is_trashed =", False)
        def contact_proc(contact):
            """"""
        return query.fetch(model_proc=contact_proc)
    
    def fetch_contacts_by_group(self, group_id):
        query = Contact.all(alias="a")
        query.select("DISTINCT")
        query.what("a.uid")
        query.what("a.creator_id")
        query.what("a.contact_name")
        query.model(ContactGroup.get_modelname(), alias="b", join="left", on="a.uid = b.contact_id")      
        query.filter("b.group_id =", group_id)
        query.order("-uid")
        query = query.filter("is_trashed =", False)
        def contact_proc(contact):
            """"""
        return query.fetch(model_proc=contact_proc)
    
    def fetch_my_groups(self, user_id, onlyrtnids=False, include_self=True):
        stmgroups = self.fetch_groups(user_id, sharetome=True, withcontactcount=False)        
        if include_self:
            groups = self.fetch_groups(user_id, withcontactcount=False)
            stmgroups.extend(groups)
        if onlyrtnids :
            gl = map(lambda x: x.key(), stmgroups)
        else:
            gl = stmgroups
        return gl
    
    def get_contactcount(self, is_trashed, user_id, group_id=None):
        query = Contact.all(alias="a")
        query.filter("a.is_trashed =", is_trashed)
        
        if group_id is not None and group_id != model.EMPTY_UID:
            query.model(ContactGroup.get_modelname(), alias="b", join="inner", on="a.uid = b.contact_id")
            query.filter("b.group_id =", group_id)
        else:
            query.filter("a.creator_id =", user_id)
            query.filter("a.uid not in", "(select contact_id from %s)" % ContactGroup.get_modelname(), wrapper=False)
        
        return query.count()
    
    def link_contact_to_user(self, contact, bind_user_account):
        if strutil.is_empty(bind_user_account):
            contact.bind_user_id = model.EMPTY_UID
            return contact
        query = Contact.all()
        usermo = user.get_user(u_account=bind_user_account)
        if usermo is None:
            raise Error("cont_error_linkusernotfound", account=bind_user_account)
        
        query.filter("bind_user_id =", usermo.key())
        query.filter("creator_id =", contact.creator_id)
        if contact.key() != None:
            query.filter("uid !=", contact.key())
        if query.count() > 0:
            raise Error("cont_error_linkuserexisted", account=bind_user_account, contactName=query.get().contact_name)
        
        contact.bind_user_id = usermo.key()
        return contact
    
    def create_contactleave(self, contactleave, modifier_id):
        contactleave.put(modifier_id)
        return contactleave
    
    def update_contactleave(self, contactleave, modifier_id):
        contactleave.put(modifier_id)
        return contactleave
    
    def delete_contactleave(self, leave_id, modifier_id):
        contactleave = ContactLeave.get_by_key(leave_id)
        contactleave.delete(modifier_id)
        return True
    
    def delete_contactleaves(self, contact_id, modifier_id):
        query = ContactLeave.all()
        query.filter("contact_id =", contact_id)
        return query.delete(modifier_id)
    
    def fetch_contactleaves(self, contact_id):
        query = ContactLeave.all()
        query.filter("contact_id =", contact_id)
        query.order("-leave_startdate")
        return query.fetch()
    
class GroupResolver(Resolver):
    
    TRASH_GROUP_ID = -100
    
    def resolve(self, query, **kwargs):
        if self._key != "gp" or self._value == None or (not isinstance(self._value, int)):
            return query
        self._value = int(self._value)
        if self._value == self.TRASH_GROUP_ID:
            query.filter("a.is_trashed =", True)
        else:
            if self._value == model.EMPTY_UID:
                query.filter("a.uid not in", "(select contact_id from %s)" % ContactGroup.get_modelname(), wrapper=False)
            else:
                alias = query.get_model_alias(ContactGroup.get_modelname())
                if alias is None:
                    query.model(ContactGroup.get_modelname(), alias="b", join="left", on="a.uid = b.contact_id")         
                query.filter("%s.group_id =" % alias, self._value)
        return query

class KeywordsResolver(Resolver):
    
    def resolve(self, query):
        if self._key != "kw":
            return query
        if self._value != None:
            query = query.filter("a.contact_name like ", ("%%%s%%" % self._value), parenthesis="(")
            query = query.filter("a.ct_company like ", ("%%%s%%" % self._value), logic="or")
            query = query.filter("a.ct_department like ", ("%%%s%%" % self._value), logic="or")
            query = query.filter("a.ct_remark like ", ("%%%s%%" % self._value), logic="or", parenthesis=")")
        return query

CONTACTRESOLVERS = [GroupResolver, KeywordsResolver]
