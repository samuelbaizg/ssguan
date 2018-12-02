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

from tornado.web import RequestHandler, StaticFileHandler

from ssguan.ignitor.base import error
from ssguan.ignitor.base.error import Error, CODE_UNKNOWN, ProgramError, \
    NoFoundError
from ssguan.ignitor.base.struct import Storage
from ssguan.ignitor.utility import kind, crypt
from ssguan.ignitor.web import config as web_config, logger
from ssguan.ignitor.web.session import Session


class Rtn(object):

    STATUS_SUCCESS = 200
    
    CONTENT_TYPE_JSON = 'application/json'

    def __init__(self, content_type=CONTENT_TYPE_JSON, data=None, e=None):
        """
            :param data|content-type wised:
                json-friendly object if content-type is application/json.
                string if content-type is text/html,text/plain,text/xml etc.
                file absolute path if content-type is image/png, image/gif,image/jpeg,etc.
                file info touple (file name, absolute path, open mode) if content-type is application/octet-stream, application/pdf,application/xml, etc.
        """
        self.__content_type = content_type
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
                self.__status = CODE_UNKNOWN
            self.__message = str(self.__e)

    @property
    def content_type(self):
        return self.__content_type
    
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
    
    def write(self, requestHandler):
        """
            Write data to web response
        """
        def write_text(requestHandler):
            requestHandler.write(self.__data)
            
        def write_json(requestHandler):
            jsonstr = kind.obj_to_json(self.to_dict())
            jsonstr = crypt.str_to_base64(jsonstr)
            requestHandler.write(jsonstr)
        
        def write_image(requestHandler):
            path = self.__data
            with open(path, 'rb') as f:
                data = f.read()
                requestHandler.write(data)
                    
        def write_stream(requestHandler):
            (name, path, mode) = self.__data
            self.set_header ('Content-Disposition', 'attachment; filename=' + name)
            with open(path, mode) as f:
                while True:
                    data = f.read(512)
                    if not data:
                        break
                    requestHandler.write(data)

        try:
            requestHandler.set_header("Content-Type", self.__content_type)
            requestHandler.set_status(Rtn.STATUS_SUCCESS)
            if self.__content_type.startswith(self.CONTENT_TYPE_JSON):
                write_json(requestHandler)
            elif self.__content_type.startswith("text/"):
                write_text(requestHandler)
            elif self.__content_type.startswith("image/"):
                write_image(requestHandler)
            else:
                write_stream(requestHandler)
        finally:            
            requestHandler.finish()
            
        
    def write_error(self, requestHandler):
        """
            Write error data to web response
        """
        def write_json(requestHandler):
            requestHandler.set_status(Rtn.STATUS_SUCCESS)
            jsonstr = kind.obj_to_json(self.to_dict())
            jsonstr = crypt.str_to_base64(jsonstr)
            requestHandler.write(jsonstr)
        
        def write_text(requestHandler):
            message = self.__message
            if self.__arguments is not None:
                for (key, value) in self.__arguments:
                    message = message.replace("{{%s}}" % key, value)
            requestHandler.set_status(self.__status, message)
            requestHandler.write(message)
            
        try:
            if self.__content_type.startswith(self.CONTENT_TYPE_JSON):
                write_json(requestHandler)
            else:
                write_text(requestHandler)
        finally:
            requestHandler.finish()
        

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
            tb_message = error.format_exc_info(exc_info)
            logger.error(tb_message)
            rtn = Rtn(e=error_class)
        except BaseException as e:
            logger.error(str(e), exc_info=1)
            rtn = Rtn(e=ProgramError(e.message))
        finally:
            rtn.write_error(self)

    def decode_arguments_body(self):
        """
            Decode request parameters if request parameters are encoded.
        """
        body = self.request.body
        data = crypt.base64_to_str(body)
        if len(data) > 0:
            data = kind.json_to_object(data)
        else:
            data = {}
        return Storage(**data)

    def decode_arguments_query(self):
        """
            Decode the parameters in querystring.
        """
        query = self.request.query  
        data = crypt.base64_to_str(query)
        if len(data) > 0:
            data = kind.json_to_object(data)
        else:
            data = {}
        return Storage(**data)

    def _gen_session(self):
        sessionConfig = web_config.get_sessionConfig()
        cookie_name = sessionConfig.cookie_name
        cookie_domain = sessionConfig.cookie_domain
        cookie_path = sessionConfig.cookie_path
        cookie_expires_days = sessionConfig.cookie_expires_days
        sid = self.get_secure_cookie(cookie_name)
        sid = kind.safestr(sid)
        ip = self.request.remote_ip
        session = Session(sid, ip, sessionConfig)
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
