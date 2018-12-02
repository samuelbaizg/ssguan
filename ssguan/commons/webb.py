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
import functools
import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, StaticFileHandler, Application

from ssguan import config
from ssguan.commons import error, loggingg
from ssguan.commons import dao, security, funcutils, typeutils
from ssguan.commons.dao import Model, UniqueValidator
from ssguan.commons.error import Error, ProgramError, NoFoundError


_logger = loggingg.get_logger(config.LOGGER_COMMONS)


class SessionExpiredError(Error):
    def __init__(self):
        super(SessionExpiredError, self).__init__(
            "Session expired, please login again.")

    @property
    def code(self):
        return 1050


class SessionInvalidError(Error):
    def __init__(self):
        super(SessionInvalidError, self).__init__(
            "Session is invalid, please login again.")

    @property
    def code(self):
        return 1051


class WrongParamError(Error):
    def __init__(self, uri, method):
        super(WrongParamError, self).__init__(
            "The parameters from uri {{uri}} with method {{method}} is not correct.", uri=uri, method=method)

    @property
    def code(self):
        return 1054


def dec_rtn(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.set_header("Content-Type", "application/json")
        data = method(self, *args, **kwargs)
        rtn = Rtn(data=data)
        self.write(rtn.to_json())
        self.finish()
    return wrapper


class Rtn(object):

    STATUS_SUCCESS = 200

    def __init__(self, data=None, e=None):
        self.__data = data
        self.__e = e
        self.__status = self.STATUS_SUCCESS
        self.__message = ""
        self.__arguments = None
        data = self.__data
        if self.__e != None:
            if isinstance(self.__e, Error):
                self.__status = self.__e.code
                self.__arguments = self.__e.arguments
            else:
                self.__status = error.CODE_UNKNOWN
            self.__message = self.__e.message

    @property
    def status(self):
        return self.__status

    @property
    def message(self):
        return self.__message

    def set_exception(self, e):
        self.__e = e

    def set_data(self, data):
        self.__data = data

    def to_dict(self):
        codedt = {}
        codedt['status'] = self.__status
        codedt['message'] = self.__message
        codedt['arguments'] = self.__arguments if self.__arguments is not None else {}
        codedt['data'] = "" if self.__data is None else self.__data
        return codedt

    def to_json(self):
        jsonstr = typeutils.obj_to_json(self.to_dict())
        jsonstr = security.str_to_base64(jsonstr)
        return jsonstr


class BaseReqHandler(RequestHandler):

    def __init__(self, *argc, **argkw):
        super(BaseReqHandler, self).__init__(*argc, **argkw)

    def prepare(self):
        self._session = self._gen_session()

    @property
    def session(self):
        return self._session

    def write_error(self, status_code, **kwargs):
        rtn = None
        try:
            exc_info = kwargs['exc_info']
            error_class = exc_info[1]
            tb_message = funcutils.format_exc_info(exc_info)
            _logger.error(tb_message)
            rtn = Rtn(e=error_class)
            # self.set_status(rtn.status, rtn.message)
            self.set_status(Rtn.STATUS_SUCCESS)
            self.write(rtn.to_json())
        except BaseException, e:
            _logger.error(e.message, exc_info=1)
            rtn = Rtn(e=ProgramError(e.message))
            # self.set_status(rtn.status, rtn.message)
            self.set_status(Rtn.STATUS_SUCCESS)
            self.write(rtn.to_json())
        finally:
            self.finish()

    def decode_arguments_body(self):
        """
            Decode request parameters if request parameters are encoded.
        """
        body = self.request.body
        data = security.base64_to_str(body)
        if len(data) > 0:
            data = typeutils.json_to_object(data)
        else:
            data = {}
        return typeutils.Storage(**data)

    def decode_arguments_uri(self):
        """
            Decode the parameters in uri.
        """
        uri = self.request.uri
        path = self.request.path
        ctx = os.path.basename(path)
        uri = uri.replace(path, "")
        if len(uri) > 0 and uri[0:1] == "?":
            uri = uri[1:]
        data = security.base64_to_str(uri)
        if len(data) > 0:
            data = typeutils.json_to_object(data)
        else:
            data = {}
        return (ctx, typeutils.Storage(**data))

    def _gen_session(self):
        session_config = config.webbCFG.get_session_configs()
        cookie_name = session_config["cookie_name"]
        cookie_domain = session_config["cookie_domain"]
        cookie_path = session_config["cookie_path"]
        cookie_expires_days = session_config["cookie_expires_days"]
        sid = self.get_secure_cookie(cookie_name)
        ip = self.request.remote_ip
        session = Session(sid, ip, session_config)
        self.set_secure_cookie(
            cookie_name, session.sid, expires_days=cookie_expires_days, domain=cookie_domain, path=cookie_path)
        return session


class URINoFoundReqHandler(BaseReqHandler):

    def prepare(self):
        raise NoFoundError("URI", self.request.uri)


class StaticFileReqHandler(StaticFileHandler):

    def write_error(self, status_code, **kwargs):
        self.finish("<html><title>%(code)d: %(message)s</title>"
                "<body>%(code)d: %(message)s</body></html>" % {
                    "code": status_code,
                    "message": self._reason,
                })


class Session(object):
    __slots__=[
        "_data", "_session_id", "_ip", "_session_config", "__getitem__", "__setitem__", "__delitem__"
    ]

    def __init__(self, session_id, ip, session_config):

        self._session_id=session_id
        self._ip=ip
        self._data=funcutils.ThreadedDict()
        self._session_config=session_config
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
            _sessiondao.update_session(self._session_id, self._data.copy())

    def __delattr__(self, name):
        delattr(self._data, name)
        _sessiondao.update_session(self._session_id, self._data.copy())

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
            rx=funcutils.re_compile('^[0-9a-fA-F]+$')
            return rx.match(session_id)

        if self._session_id and not __valid_session_id(self._session_id):
            self._session_id=None

        _sessiondao.cleanup(self._session_config["timeout"])

        if self._session_id:
            session=_sessiondao.get_session(self._session_id)
            if session is not None:
                if not self._session_config["ignore_change_ip"] and self._ip != session.ip:
                    raise SessionInvalidError()
                self._data.update(**_sessiondao.decode(session.data))
                _sessiondao.access_session(self._session_id)
            # session_id can't be found in store means session expired
            else:
                self._session_id=None

        if self._session_id is None:
            self._session_id=self._generate_session_id()
            _sessiondao.create_session(
                self._session_id, self._data.copy(), self._ip)

    def _generate_session_id(self):
        while True:
            rand=os.urandom(16)
            now=datetime.time()
            secret_key=self._session_config["secret_key"]
            ip=self._ip
            session_id=security.str_to_sha1_hex("%s%s%s%s" % (
                rand, now, typeutils.safestr(ip), secret_key))
            if not _sessiondao.exist_session(session_id):
                break
        return session_id


class WebSession(Model):

    @classmethod
    def meta_domain(cls):
        return config.MODULE_WEBB

    session_id=dao.StringProperty(
        "sessionId", required=True, length=128, validator=UniqueValidator("session_id"))
    access_time=dao.DateTimeProperty("accessTime", required=True)
    data=dao.StringProperty("data", required=False, length=65535)


class _SessionDao(object):

    def create_session(self, session_id, data, ip):
        session=WebSession()
        session.session_id=session_id
        session.access_time=typeutils.utcnow()
        data='' if data is None else data
        session.data=self.encode(data)
        session.ip=ip
        session=session.create(None)
        return session

    def update_session(self, session_id, data):
        query=WebSession.all()
        query.filter("session_id =", session_id)
        session=query.get()
        if session == None:
            raise SessionInvalidError()
        session.access_time=typeutils.utcnow()
        data='' if data is None else data
        session.data=self.encode(data)
        session.update(None)
        return session

    def access_session(self, session_id):
        query=WebSession.all()
        query.filter("session_id =", session_id)
        session=query.get()
        if session == None:
            raise SessionInvalidError()
        session.access_time=typeutils.utcnow()
        session.update(None)
        return session

    def cleanup(self, timeout):
        # timedelta takes numdays as arg
        timeout=datetime.timedelta(seconds=timeout)
        last_allowed_time=typeutils.utcnow() - timeout
        query=WebSession.all()
        query.filter("access_time <=", last_allowed_time)
        query.delete(None)
        return True

    def exist_session(self, session_id):
        query=WebSession.all()
        query.filter("session_id =", session_id)
        return query.count() > 0

    def get_session(self, session_id):
        query=WebSession.all()
        query.filter("session_id =", session_id)
        session=query.get()
        return session

    def encode(self, session_dict):
        pickled=typeutils.obj_to_pickle(session_dict)
        return security.str_to_base64(pickled)

    def decode(self, session_data):
        pickled=security.base64_to_str(session_data)
        return typeutils.pickle_to_obj(pickled)


_sessiondao=_SessionDao()


class WebApp(Application):
    def __init__(self, host, handlers, **settings):
        super(WebApp, self).__init__(
            handlers=handlers, default_host=host, **settings)


def startup(host, port, *args, **kwargs):
    """
        Start web server with host:port
    """
    webapp=WebApp(host, config.webbCFG.get_handlers(),
                    **config.webbCFG.get_settings())
    http_server=HTTPServer(webapp)
    http_server.listen(port)
    _logger.info("web is running on %s:%s", host, port)
    IOLoop.current().start()


def uninstall_module():
    WebSession.delete_schema()
    from ssguan.modules import sysprop
    sysprop.delete_sysprops(config.MODULE_WEBB, None, config.ID_SYSTEM)
    config.dbCFG.delete_model_dbkey("%s_*" % config.MODULE_WEBB)
    return True


def install_module():
    WebSession.create_schema()
    config.dbCFG.add_model_dbkey(
        "%s_*" % config.MODULE_WEBB, config.dbCFG.ROOT_DBKEY)

    config.webbCFG.add_session_config("cookie_name", "pid")
    config.webbCFG.add_session_config("cookie_domain", "/")
    config.webbCFG.add_session_config("cookie_path", "/")
    config.webbCFG.add_session_config("cookie_expires_days", 30)

    # 24 * 60 * 60 ( 24 hours in seconds )
    config.webbCFG.add_session_config("timeout", 24 * 60 * 60)
    config.webbCFG.add_session_config("ignore_change_ip", True)
    config.webbCFG.add_session_config("secret_key", "4D2eGc537aEf07c05Aj0")

    config.webbCFG.add_setting("autoreload", False)
    config.webbCFG.add_setting("debug", True)
    config.webbCFG.add_setting("static_path", os.path.join(
        os.path.dirname(__file__), "..", "webui", "public"))
    config.webbCFG.add_setting(
        "static_handler_class", "ssguan.commons.webb.StaticFileReqHandler")
    config.webbCFG.add_setting(
        "notfound_handler_class", "ssguan.commons.webb.URINoFoundReqHandler")
    config.webbCFG.add_setting("cookie_secret", "4D2eGc537aEf07c05Aj0")
    config.webbCFG.add_setting("route_context", "/api")
    return True
