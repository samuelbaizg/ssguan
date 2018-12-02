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
import urllib

import chardet
from requests import cookies
from requests.cookies import MockRequest
import six
import tornado
from tornado.httpclient import HTTPClient

from six.moves import http_cookies
from six.moves.urllib.parse import urljoin, urlsplit
from ssguan.ignitor.utility import kind


class _HTTPClient(HTTPClient):
    def is_closed(self):
        return self._closed
    

class HttpClientPool(object):
        def __init__(self):
            self._connections = None
        
        def get_httpclient(self):         
            return self.__new_httpclient()
            
        def __new_httpclient(self):
            hc = _HTTPClient()
            return hc
        
__hcPool = HttpClientPool()

class Response(object):
    
    def __init__(self, status, content, encoding, url, orig_url, time, headers={}, cookies={}, error=None):
        self._status_code = status
        self._content = content
        self._encoding = encoding
        self._headers = headers
        self._cookies = cookies
        self._time = time
        self._url = url
        self._orig_url = orig_url
        self._error = error
        self._unicontent = kind.safestr(self._content, self._encoding)
    
    @property
    def status_code(self):
        return self._status_code
    
    @property
    def content(self):
        """
            the original content without encoding conversion
        """
        return self._content
    
    @property
    def encoding(self):
        """
            The original encoding of the content
        """
        return self._encoding
    
    @property
    def unicontent(self):
        return self._unicontent
    
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
    def header_content_type(self):
        return self._headers["Content-Type"]
    
    @property
    def header_content_length(self):
        return self._headers["Content-Length"]
    
    def to_unidict(self):
        """
            Convert the json unicode content to an object.
        """
        return kind.json_to_object(self._unicontent)
    
ALLOWED_OPTIONS = ['method', 'data', 'timeout', 'cookies', 'use_gzip']
DEFAULT_OPTIONS = {
    'method': 'GET',
    'headers': {},
    'use_gzip': True,
    'timeout': 120
}

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
    
def get_httpclient():
    return __hcPool.get_httpclient()

def send_request(url, headers={}, options={}, user_agent=None, proxy=None, httpclient=None):
    '''HTTP fetcher
    :param proxy|str: the format is "http://username:password@host:port" or "username:password@host:port"
    :param options|dict: the fetch options includes 'method', 'timeout', 'cookies', 'use_gzip', 'etag','last_modified', 'max_redirects', 'data'
    
    '''
    start_time = time.time()
    headers = headers if headers is not None else {}
    options = options if options is not None else {}

    fetch = copy.deepcopy(DEFAULT_OPTIONS)
    fetch['url'] = url
    fetch['headers']['User-Agent'] = user_agent if user_agent is not None else ''
    for each in ALLOWED_OPTIONS:
        if each in options:
            fetch[each] = options[each]
    fetch['headers'].update(headers)

    # proxy
    proxy_string = None
    if proxy is not None:
        proxy_string = proxy
    if proxy_string is not None:
        if '://' not in proxy_string:
            proxy = 'http://' + proxy_string
        proxy_splited = urlsplit(proxy)
        if proxy_splited.username:
            fetch['proxy_username'] = proxy_splited.username               
        if proxy_splited.password:
            fetch['proxy_password'] = proxy_splited.password                
        fetch['proxy_host'] = proxy_splited.hostname            
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
            c.load(kind.unibytes(fetch['headers']['Cookie']))
        for key in c:
            session.set(key, c[key])
        del fetch['headers']['Cookie']
    fetch['follow_redirects'] = False
    if 'timeout' in fetch:
        fetch['connect_timeout'] = fetch['request_timeout'] = fetch['timeout']
        del fetch['timeout']
    if 'data' in fetch:
        da = fetch['data']
        if type(da) == dict:
            dastr = urllib.parse.urlencode(da, doseq=True)
        else:
            dastr = str(da)
        fetch['body'] = dastr 
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
            error = kind.safestr(response.error)
        body = response.body or ''
        chardit1 = chardet.detect(body)['encoding']
        result = Response(response.code,
                        body,
                        chardit1,
                        response.effective_url or url,
                        url,
                        time.time() - start_time,
                        headers=dict(response.headers),
                        cookies=session.get_dict(),
                        error=error
                        )
        
        return result
    
    def handle_error(error):
        result = Response(getattr(error, 'code', 599),
                        '',
                        url,
                        url,
                        time.time() - start_time,
                        headers={},
                        cookies={},
                        error=kind.safestr(error)
                        )
        return result
    
    def make_request(fetch, httpclient=None):
        try:
            request = tornado.httpclient.HTTPRequest(**fetch)
            cookie_header = cookies.get_cookie_header(session, request)
            if cookie_header:
                request.headers['Cookie'] = cookie_header
            if httpclient is None:
                httpclient = __hcPool.get_httpclient()
                response = handle_response(httpclient.fetch(request))
                httpclient.close()
            else:
                response = handle_response(httpclient.fetch(request))
            return response                
        except tornado.httpclient.HTTPError as e:
            if e.response:
                return handle_response(e.response)
            else:
                return handle_error(e)
        except Exception as e:
            return handle_error(e)

    return make_request(fetch, httpclient=httpclient)
      
