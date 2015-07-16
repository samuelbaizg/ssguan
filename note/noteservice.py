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
from contact.contactservice import ContactService
from core import tag, filex, model
from core.error import Error
from core.model import EMPTY_UID, Resolver
from core.service import Service
from notemodel import  Notebook, Note


class NoteService(Service):
    
    def create_notebook(self, notebook, modifier_id):
        query = Notebook.all()
        query.order("-nb_order")
        if query.count() > 0:
            notebook.nb_order = query.get().nb_order + 1
        else:
            notebook.nb_order = 1
        notebook.put(modifier_id)
        return notebook
    
    def update_notebook(self, notebook, modifier_id):
        notebook.put(modifier_id)
        return notebook
        
    def delete_notebook(self, notebook_id, modifier_id):
        notebook = Notebook.get_by_key(notebook_id)
        notebook.delete(modifier_id)
        query = Note.all()
        query.filter("notebook_id =", notebook_id)
        query.set("notebook_id", EMPTY_UID)
        query.set("is_trashed", True)
        query.update(modifier_id)
        query = Notebook.all()
        return True
    
    def get_notebook(self, notebook_id):
        notebook = Notebook.get_by_key(notebook_id)
        return notebook
    
    def fetch_notebooks(self, user_id, sharetome=None, withnotecount=True):
        query = Notebook.all()
        if sharetome:
            group_ids = ContactService.get_instance().fetch_my_groups(user_id, onlyrtnids=True, include_self=False)
            if len(group_ids) > 0:
                query.filter("group_id in", group_ids)
            else:
                return []
        else:
            query.filter("creator_id =", user_id)
        query.order("nb_order")
        
        def notebook_proc(notebook):
            if withnotecount:
                notebook.notecount = self.get_notecount(False, user_id, notebook_id=notebook.uid)
        
        notebooks = query.fetch(model_proc=notebook_proc)
        return notebooks
    
    def fetch_my_notebooks(self, user_id, onlyrtnids=False, include_self=True):
        stmnotebooks = self.fetch_notebooks(user_id, sharetome=True, withnotecount=False)
        if include_self:
            notebooks = self.fetch_notebooks(user_id, withnotecount=False)
            stmnotebooks.extend(notebooks)
        if onlyrtnids:
            nkl = map(lambda x: x.key(), stmnotebooks)
        else:
            nkl = stmnotebooks
        return nkl
    
    def create_note(self, note, modifier_id):
        note.is_trashed = False
        note.put(modifier_id)
        return note
    
    def update_note(self, note, modifier_id):
        nt = Note.get_by_key(note.uid)
        if note.creator_id != modifier_id and nt.notebook_id != note.notebook_id:
            raise Error("note_error_movesharednote")
        if nt.is_trashed : 
            raise Error("note_error_trashed_update")
        note.put(modifier_id)
        return note
    
    def recover_note(self, note_id, notebook_id, modifier_id):
        note = Note.get_by_key(note_id)
        note.is_trashed = False
        note.notebook_id = notebook_id
        note.put(modifier_id)
        return note
    
    def move_note(self, note_id, notebook_id, modifier_id):
        note = Note.get_by_key(note_id)
        note.notebook_id = int(notebook_id)
        note.put(modifier_id)
        return note
    
    def get_note(self, note_id):
        note = Note.get_by_key(note_id)
        return note
            
    def trash_notes(self, note_ids, is_trashed, modifier_id):
        for note_id in note_ids:
            note = Note.get_by_key(note_id)
            note.is_trashed = is_trashed
            note.put(modifier_id)
        return True
    
    def empty_trash(self, user_id, modifier_id):
        query = Note.all()
        query.filter("is_trashed =", True)
        query.filter("creator_id =", user_id)
        status = query.delete(modifier_id)
        return status
    
    def delete_note(self, note_id, modifier_id):
        note = Note.get_by_key(int(note_id))
        if note.is_trashed:
            tag.delete_tagmodels(modifier_id, model_nk=(Note.get_modelname(), note.uid), modifier_id=modifier_id)
            filex.delete_files(note.creator_id, model_nk=(Note.get_modelname(), note.uid), modifier_id=modifier_id)
            note.delete(modifier_id)
        else:
            if note.creator_id != modifier_id:
                raise Error("note_error_deletesharednote")
            self.trash_notes([note.uid], True, modifier_id)
        return True
    
    def fetch_notes(self, user_id, filters=None, limit=20, offset=0):
        
        def append_filters(query):
            for ft in filters:
                for (key, value) in ft.items():
                    for nr in NOTERESOLVERS:
                        nrinst = nr(key, value)
                        query.extend(nrinst)
                    
        query = Note.all(alias="a")
        query.select("DISTINCT")
        query.order("-a.uid")
        
        notebook_ids = self.fetch_my_notebooks(user_id, onlyrtnids=True)
        if len(notebook_ids) > 0:
            query.filter("a.notebook_id in", notebook_ids, parenthesis="(")
            query.filter("a.creator_id =", user_id, logic="or", parenthesis=")")
        else:
            query.filter("a.creator_id =", user_id)
        
        if filters is not None:
            append_filters(query)
            
        if not query.has_filter("a.is_trashed"):
            query = query.filter("a.is_trashed =", False)
            
        def note_proc(note):
            ''''''
        
        return query.fetch(limit, offset, paging=True, model_proc=note_proc)
    
    def get_notecount(self, is_trashed, user_id, notebook_id=None):
        query = Note.all()
        query.filter("is_trashed =", is_trashed)
        if notebook_id != None and notebook_id != model.EMPTY_UID:
            query.filter("notebook_id =", notebook_id)
        elif notebook_id == model.EMPTY_UID:
            query.filter("notebook_id =", notebook_id)
            query.filter("creator_id =", user_id)
        else:
            query.filter("creator_id =", user_id)
        if notebook_id != None:
            query.filter("notebook_id =", notebook_id)
        return query.count()
        


class NotebookResolver(Resolver):
    
    TRASH_NOTEBOOK_ID = -100
    
    def resolve(self, query, **kwargs):
        if self._key != "nb" or self._value == None or (not isinstance(self._value, int)):
            return query
        self._value = int(self._value)
        if self._value == self.TRASH_NOTEBOOK_ID:
            query.filter("a.is_trashed =", True)            
        else:
            query.filter("a.notebook_id =", self._value)
        return query

class KeywordsResolver(Resolver):
    
    def resolve(self, query):
        if self._key != "kw":
            return query
        if self._value != None:
            query = query.filter("a.n_subject like ", ("%%%s%%" % self._value), parenthesis="(")
            query = query.filter("a.n_content like ", ("%%%s%%" % self._value), logic="or", parenthesis=")")
        return query       

NOTERESOLVERS = [NotebookResolver, KeywordsResolver]
