'''
Created on Jan 1st, 2015

@author: samuelbaizg@gmail.com
@copyright: www.suishouguan.com

'''
import conf
from contact.contactmodel import Contact, Group, GroupVersion, GroupComponent, \
    GroupException, ContactGroup, ContactLeave
from contact.contactservice import ContactService
from core import jsonutil, i18n
from core import strutil, model
from core.handler import Handler
from core.model import stdModel
import web


class GroupResourceSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        contactgroup = self._get_model_parameter(ContactGroup)
        if strutil.is_empty(contactgroup.key()):
            contactgroup.creator_id = self._get_user_id()
            contactgroup = ContactService.get_instance().create_contactgroup(contactgroup, self._get_user_id())
        else:
            contactgroup = ContactService.get_instance().update_contactgroup(contactgroup, self._get_user_id())
        rtn.set_data(contactgroup)
        return rtn.to_json()

class GroupResourceDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        resource_id = self._get_int_parameter("resourceKey")
        status = ContactService.get_instance().delete_contactgroup(resource_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class GroupResourceListHandler(Handler):
    
    def execute(self):        
        rtn = self._new_rtn()
        group_id = self._get_int_parameter("groupKey")
        groupresources = ContactService.get_instance().fetch_contactgroups(group_id=group_id)
        std = stdModel()
        std.groupResources = groupresources
        std.contacts = ContactService.get_instance().fetch_contacts_created_by(self._get_user_id())
        rtn.set_data(std)
        return rtn.to_json()



class GroupExceptionSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        groupworkexception = self._get_model_parameter(GroupException)
        if strutil.is_empty(groupworkexception.key()):
            groupworkexception.creator_id = self._get_user_id()
            groupworkexception = ContactService.get_instance().create_groupexception(groupworkexception, self._get_user_id())
        else:
            groupworkexception = ContactService.get_instance().update_groupexception(groupworkexception, self._get_user_id())
        rtn.set_data(groupworkexception)
        return rtn.to_json()

class GroupExceptionDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        exception_id = self._get_int_parameter("exceptionKey")
        status = ContactService.get_instance().delete_groupexception(exception_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class GroupExceptionListHandler(Handler):
    
    def execute(self):        
        rtn = self._new_rtn()
        group_id = self._get_int_parameter("groupKey")
        groupversions = ContactService.get_instance().fetch_groupexceptions(group_id)
        rtn.set_data(groupversions)
        return rtn.to_json()

class GroupVersionSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        groupversion = self._get_model_parameter(GroupVersion)
        if strutil.is_empty(groupversion.key()):
            groupversion.creator_id = self._get_user_id()
            groupversion = ContactService.get_instance().create_groupversion(groupversion, self._get_user_id())
        else:
            groupversion = ContactService.get_instance().update_groupversion(groupversion, self._get_user_id())
        rtn.set_data(groupversion)
        return rtn.to_json()

class GroupVersionDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        version_id = self._get_int_parameter("versionKey")
        status = ContactService.get_instance().delete_groupversion(version_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class GroupVersionListHandler(Handler):
    
    def execute(self):        
        rtn = self._new_rtn()
        group_id = self._get_int_parameter("groupKey")
        groupversions = ContactService.get_instance().fetch_groupversions(group_id)
        rtn.set_data(groupversions)
        return rtn.to_json()
    
class GroupComponentSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        groupcomponent = self._get_model_parameter(GroupComponent)
        if strutil.is_empty(groupcomponent.key()):
            groupcomponent.creator_id = self._get_user_id()
            groupcomponent = ContactService.get_instance().create_groupcomponent(groupcomponent, self._get_user_id())
        else:
            groupcomponent = ContactService.get_instance().update_groupcomponent(groupcomponent, self._get_user_id())
        rtn.set_data(groupcomponent)
        return rtn.to_json()

class GroupComponentDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        component_id = self._get_int_parameter("componentKey")
        status = ContactService.get_instance().delete_groupcomponent(component_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class GroupComponentListHandler(Handler):
    
    def execute(self):        
        rtn = self._new_rtn()
        group_id = self._get_int_parameter("groupKey")
        groupcomponents = ContactService.get_instance().fetch_groupcomponents(group_id)
        rtn.set_data(groupcomponents)
        return rtn.to_json()

class GroupSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        group = self._get_model_parameter(Group)
        if strutil.is_empty(group.key()):
            group.creator_id = self._get_user_id()
            group = ContactService.get_instance().create_group(group, self._get_user_id())
        else:
            group = ContactService.get_instance().update_group(group, self._get_user_id())
        rtn.set_data(group)
        return rtn.to_json()

class GroupDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        group_id = self._get_int_parameter("groupKey")
        status = ContactService.get_instance().delete_group(group_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class ContactEmptyTrashHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        status = ContactService.get_instance().empty_trash(self._get_user_id(), self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class GroupListHandler(Handler):
    
    def execute(self):        
        rtn = self._new_rtn()
        
        std = stdModel()
        select = self._get_bool_parameter("select", False)
        if not select:
            groups = ContactService.get_instance().fetch_groups(self._get_user_id())
            std.groups = groups;
            defaultgroup = Group()
            defaultgroup.uid = model.EMPTY_UID
            defaultgroup.group_name = i18n.get_i18n_message(conf.get_preferred_language(), "cont_label_defaultgroup")
            defaultgroup.contactcount = ContactService.get_instance().get_contactcount(False, self._get_user_id(), group_id=model.EMPTY_UID)
            defaultgroup.creator_id = self._get_user_id()
            groups.insert(0, defaultgroup);
            
            trash = Group()
            trash.uid = -100
            trash.group_name = i18n.get_i18n_message(conf.get_preferred_language(), "cont_label_recyclebin")
            trash.contactcount = ContactService.get_instance().get_contactcount(True, self._get_user_id())
            trash.creator_id = self._get_user_id()
            groups.append(trash)
            
            stmgroups = ContactService.get_instance().fetch_groups(self._get_user_id(), sharetome=True)
            std.groups.extend(stmgroups)
        else:
            groups = ContactService.get_instance().fetch_groups(self._get_user_id(), withcontactcount=False)
            std.groups = groups;
        rtn.set_data(std)
        return rtn.to_json()

class ContactListHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        offset = self._get_int_parameter('offset', 1)
        limit = self._get_int_parameter('limit', 20)
        filters = self._get_str_parameter('filters')
        filters = jsonutil.to_dict(filters)
        pager = ContactService.get_instance().fetch_contacts(self._get_user_id(), filters=filters, limit=limit, offset=offset)
        rtn.set_data(pager)
        return rtn.to_json()
        
class ContactSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        contact = self._get_model_parameter(Contact)
        group_ids = self._get_str_parameter("groupKeys", default='')
        group_ids = map(int, group_ids.split(",")) if group_ids.strip() != '' else []
        contact.group_ids = group_ids
        if strutil.is_empty(contact.key()):
            contact.creator_id = self._get_user_id()
            contact = ContactService.get_instance().create_contact(contact, self._get_user_id())
        else:
            contact = ContactService.get_instance().update_contact(contact, self._get_user_id())
        contact.contactLeaves = ContactService.get_instance().fetch_contactleaves(contact.key())
        rtn.set_data(contact)
        return rtn.to_json()

class ContactDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        contact_id = self._get_int_parameter("contactKey")
        status = ContactService.get_instance().delete_contact(contact_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class ContactRecoverHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        contact_id = self._get_int_parameter("contactKey")
        status = ContactService.get_instance().recover_contact(contact_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()
    
    
class ContactLeaveSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        contactleave = self._get_model_parameter(ContactLeave)
        if strutil.is_empty(contactleave.key()):
            contactleave.creator_id = self._get_user_id()
            contactleave = ContactService.get_instance().create_contactleave(contactleave, self._get_user_id())
        else:
            contactleave = ContactService.get_instance().update_contactleave(contactleave, self._get_user_id())
        rtn.set_data(contactleave)
        return rtn.to_json()

class ContactLeaveDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        leave_id = self._get_int_parameter("leaveKey")
        status = ContactService.get_instance().delete_contactleave(leave_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()
