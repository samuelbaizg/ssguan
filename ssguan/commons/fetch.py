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
import copy
import time

from requests import cookies
import six
import tornado
from tornado.curl_httpclient import CurlAsyncHTTPClient

from requests.cookies import MockRequest
from six.moves import http_cookies
from six.moves.urllib.parse import urljoin, urlsplit
from ssguan import config
from ssguan.commons import typeutils, loggingg


_logger = loggingg.get_logger(config.LOGGER_COMMONS)

class _CurlAsyncHTTPClient(CurlAsyncHTTPClient):

    def free_size(self):
        return len(self._free_list)

    def size(self):
        return len(self._curls) - self.free_size()
    
class Result(object):
    
    def __init__(self, status, content, url, orig_url, time, headers={}, cookies={}, error=None):
        self._status_code = status
        self._content = content
        self._headers = headers
        self._cookies = cookies
        self._time = time
        self._url = url
        self._orig_url = orig_url
        self._error = error
    
    @property
    def status_code(self):
        return self._status_code
    
    @property
    def content(self):
        return self._content
    
    @property
    def headers(self):
        return self._headers
    
    @property
    def cookies(self):
        return self._cookies
    
    @property
    def time(self):
        return self._time
    
    @property
    def url(self):
        return self._url
    
    @property
    def orig_url(self):
        return self._orig_url
    
    @property
    def content_json(self):
        return typeutils.json_to_object(self._content)
    
    @property
    def header_content_type(self):
        return self._headers["Content-Type"]
    
    @property
    def header_content_length(self):
        return self._headers["Content-Length"]
    
class Fetcher(object):
    
    TYPE_HTTP = 'http'
    
    ALLOWED_OPTIONS = ['method', 'data', 'timeout', 'cookies', 'use_gzip']
    DEFAULT_OPTIONS = {
        'method': 'GET',
        'headers': {},
        'use_gzip': True,
        'timeout': 120
    }
    
    def __init__(self, user_agent='', pool_size=100, proxy=None, async=True, io_loop=None):
        self._user_agent = user_agent
        self._proxy = proxy
        self._async = async
        self._pool_size = pool_size
        if self._async:
            if io_loop is None:
                io_loop = tornado.ioloop.IOLoop()
            self._http_client = _CurlAsyncHTTPClient(max_clients=self._pool_size,
                                                     io_loop=io_loop)
        else:
            self._http_client = tornado.httpclient.HTTPClient(
                _CurlAsyncHTTPClient, max_clients=self._pool_size
            )

    def http_fetch(self, url, callback, headers={}, options={}):
        '''HTTP fetcher
        :param callback|function: the parameter of function is instance of class Result
        :param proxy|str: the format is "http://username:password@host:port" or "username:password@host:port"
        :param options|dict: the fetch options includes 'method', 'timeout', 'cookies', 'use_gzip', 'etag','last_modified', 'max_redirects'
        
        '''
        start_time = time.time()
        headers = headers if headers is not None else {}
        options = options if options is not None else {}
    
        fetch = copy.deepcopy(self.DEFAULT_OPTIONS)
        fetch['url'] = url
        fetch['headers']['User-Agent'] = self._user_agent
        for each in self.ALLOWED_OPTIONS:
            if each in options:
                fetch[each] = options[each]
        fetch['headers'].update(headers)
    
        # proxy
        proxy_string = None
        if self._proxy is not None:
            proxy_string = self._proxy
        if proxy_string is not None:
            if '://' not in proxy_string:
                proxy = 'http://' + proxy_string
            proxy_splited = urlsplit(proxy)
            if proxy_splited.username:
                fetch['proxy_username'] = proxy_splited.username
                if six.PY2:
                    fetch['proxy_username'] = fetch['proxy_username'].encode('utf8')
            if proxy_splited.password:
                fetch['proxy_password'] = proxy_splited.password
                if six.PY2:
                    fetch['proxy_password'] = fetch['proxy_password'].encode('utf8')
            fetch['proxy_host'] = proxy_splited.hostname.encode('utf8')
            if six.PY2:
                fetch['proxy_host'] = fetch['proxy_host'].encode('utf8')
            fetch['proxy_port'] = proxy_splited.port or 8080
    
        # etag
        if options.get('etag', True):
            t = None
            if isinstance(options.get('etag'), six.string_types):
                t = options.get('etag')
            if t:
                fetch['headers'].setdefault('If-None-Match', t)
        # last modifed
        if options.get('last_modified', True):
            t = None
            if isinstance(options.get('last_modifed'), six.string_types):
                t = options.get('last_modifed')
            if t:
                fetch['headers'].setdefault('If-Modified-Since', t)
    
        session = cookies.RequestsCookieJar()
    
        # fix for tornado request obj
        fetch['headers'] = tornado.httputil.HTTPHeaders(fetch['headers'])
        if 'Cookie' in fetch['headers']:
            c = http_cookies.SimpleCookie()
            try:
                c.load(fetch['headers']['Cookie'])
            except AttributeError:
                c.load(typeutils.utf8(fetch['headers']['Cookie']))
            for key in c:
                session.set(key, c[key])
            del fetch['headers']['Cookie']
        fetch['follow_redirects'] = False
        if 'timeout' in fetch:
            fetch['connect_timeout'] = fetch['request_timeout'] = fetch['timeout']
            del fetch['timeout']
        if 'data' in fetch:
            fetch['body'] = fetch['data']
            del fetch['data']
        if 'cookies' in fetch:
            session.update(fetch['cookies'])
            del fetch['cookies']
    
        store = {}
        store['max_redirects'] = options.get('max_redirects', 5)
    
        def handle_response(response):
            extract_cookies_to_jar(session, response.request, response.headers)
            if (response.code in (301, 302, 303, 307)
                    and response.headers.get('Location')
                    and options.get('allow_redirects', True)):
                if store['max_redirects'] <= 0:
                    error = tornado.httpclient.HTTPError(
                        599, 'Maximum (%d) redirects followed' % options.get('max_redirects', 5),
                        response)
                    return handle_error(error)
                if response.code in (302, 303):
                    fetch['method'] = 'GET'
                    if 'body' in fetch:
                        del fetch['body']
                fetch['url'] = urljoin(fetch['url'], response.headers['Location'])
                fetch['request_timeout'] -= time.time() - start_time
                if fetch['request_timeout'] < 0:
                    fetch['request_timeout'] = 0.1
                fetch['connect_timeout'] = fetch['request_timeout']
                store['max_redirects'] -= 1
                return make_request(fetch)
    
            error = ''
            if response.error:
                error = typeutils.text(response.error)
            result = Result(response.code,
                            response.body or '',
                            response.effective_url or url,
                            url,
                            time.time() - start_time,
                            headers=dict(response.headers),
                            cookies=session.get_dict(),
                            error=error
                            )
            if 200 <= response.code < 300:
                _logger.info("[%d] %s %.2fs", response.code,
                            url, result.time)
            else:
                _logger.warning("[%d] %s %.2fs", response.code,
                               url, result.time)
            
            callback(result)
            return result
    
        handle_error = lambda x: self.handle_error(self.TYPE_HTTP,
                                                   url, start_time, callback, x)
    
        def make_request(fetch):
            try:
                request = tornado.httpclient.HTTPRequest(**fetch)
                cookie_header = cookies.get_cookie_header(session, request)
                if cookie_header:
                    request.headers['Cookie'] = cookie_header
                if self._async:
                    self._http_client.fetch(request, handle_response)
                else:
                    return handle_response(self._http_client.fetch(request))
            except tornado.httpclient.HTTPError as e:
                if e.response:
                    return handle_response(e.response)
                else:
                    return handle_error(e)
            except Exception as e:
                _logger.exception(fetch)
                return handle_error(e)
    
        return make_request(fetch)

    def handle_error(self, type1, url, start_time, callback, error):
        result = Result(getattr(error, 'code', 599),
                            '',
                            url,
                            url,
                            time.time() - start_time,
                            headers={},
                            cookies={},
                            error=typeutils.text(error)
                            )
        _logger.error("[%d] %s, %r %.2fs", result.status_code, url, error, result.time)
        callback(result)
        return result

class MockResponse(object):
    def __init__(self, headers):
        self._headers = headers

    def info(self):
        return self

    def getheaders(self, name):
        """make cookie python 2 version use this method to get cookie list"""
        return self._headers.get_list(name)

    def get_all(self, name, default=[]):
        """make cookie python 3 version use this instead of getheaders"""
        return self._headers.get_list(name) or default
        
def extract_cookies_to_jar(jar, request, response):
    req = MockRequest(request)
    res = MockResponse(response)
    jar.extract_cookies(res, req)
