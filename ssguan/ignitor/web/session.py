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

import datetime
import os

from ssguan.ignitor import IGNITOR_DOMAIN
from ssguan.ignitor.base.struct import ThreadedDict
from ssguan.ignitor.orm import properti
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.orm.validator import UniqueValidator
from ssguan.ignitor.utility import crypt, kind
from ssguan.ignitor.web.error import SessionInvalidError


class Session(object):
    
    __slots__ = [
        "_data", "_session_id", "_ip", "_sessionConfig"
    ]

    def __init__(self, session_id, ip, sessionConfig):

        self._session_id = session_id
        self._ip = ip
        self._data = ThreadedDict()
        self._sessionConfig = sessionConfig
        self._load()

    def __contains__(self, name):
        return name in self._data

    def __getattr__(self, name):
        return getattr(self._data, name)

    def __setattr__(self, name, value):
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            setattr(self._data, name, value)
            _sessionDao.update_session(self._session_id, self._data.copy())

    def __delattr__(self, name):
        delattr(self._data, name)
        _sessionDao.update_session(self._session_id, self._data.copy())

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)

    def __delitem__(self, name):
        self.__delattr__(name)

    @property
    def sid(self):
        return self._session_id

    def _load(self):
        """ return False if a new session is created
        """
        def __valid_session_id(session_id):
            rx = kind.re_compile('^[0-9a-fA-F]+$')
            return rx.match(session_id)

        if self._session_id and not __valid_session_id(self._session_id):
            self._session_id = None

        _sessionDao.cleanup(self._sessionConfig.timeout)

        if self._session_id:
            session = _sessionDao.get_session(self._session_id)
            if session is not None:
                if not self._sessionConfig.ignore_change_ip and self._ip != session.ip:
                    raise SessionInvalidError()
                self._data.update(**_sessionDao.decode(session.data))
                _sessionDao.access_session(self._session_id)
            # session_id can't be found in store means session expired
            else:
                self._session_id = None

        if self._session_id is None:
            self._session_id = self._generate_session_id()
            _sessionDao.create_session(
                self._session_id, self._data.copy(), self._ip)

    def _generate_session_id(self):
        while True:
            rand = os.urandom(16)
            now = datetime.time()
            secret_key = self._sessionConfig.secret_key
            ip = self._ip
            session_id = crypt.str_to_sha1_hex("%s%s%s%s" % (
                rand, now, ip, secret_key))
            if not _sessionDao.exist_session(session_id):
                break
        return session_id


class WebSession(Model):

    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN

    session_id = properti.StringProperty(required=True, length=128, validator=UniqueValidator("session_id"))
    access_time = properti.DateTimeProperty(required=True)
    data = properti.StringProperty(required=False, length=65535)


class _SessionDao(object):

    def create_session(self, session_id, data, ip):
        session = WebSession()
        session.session_id = session_id
        session.access_time = kind.utcnow()
        data = '' if data is None else data
        session.data = self.encode(data)
        session.ip = ip
        session = session.create(None)
        return session

    def update_session(self, session_id, data):
        query = WebSession.all()
        query.filter("session_id =", session_id)
        session = query.get()
        if session == None:
            raise SessionInvalidError()
        session.access_time = kind.utcnow()
        data = '' if data is None else data
        session.data = self.encode(data)
        session.update(None)
        return session

    def access_session(self, session_id):
        query = WebSession.all()
        query.filter("session_id =", session_id)
        session = query.get()
        if session == None:
            raise SessionInvalidError()
        session.access_time = kind.utcnow()
        session.update(None)
        return session

    def cleanup(self, timeout):
        # timedelta takes numdays as arg
        timeout = datetime.timedelta(seconds=timeout)
        last_allowed_time = kind.utcnow() - timeout
        query = WebSession.all()
        query.filter("access_time <=", last_allowed_time)
        query.delete(None)
        return True

    def exist_session(self, session_id):
        query = WebSession.all()
        query.filter("session_id =", session_id)
        return query.count() > 0

    def get_session(self, session_id):
        query = WebSession.all()
        query.filter("session_id =", session_id)
        session = query.get()
        return session

    def encode(self, session_dict):
        pickled = kind.obj_to_pickle(session_dict)
        return crypt.str_to_base64(pickled)

    def decode(self, session_data):
        pickled = crypt.base64_to_str(session_data)
        return kind.pickle_to_obj(pickled)


_sessionDao = _SessionDao()
