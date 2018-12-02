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

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

from ssguan.ignitor.web import config as web_config, logger


class WebApp(Application):
    def __init__(self, host, handlers, **settings):
        super(WebApp, self).__init__(
            handlers=handlers, default_host=host, **settings)

def startup(host, port, *args, **kwargs):
    """
        Start web server with host:port
    """
    webapp=WebApp(host, web_config.get_handlers(),
                    **web_config.get_settings())
    http_server=HTTPServer(webapp)
    http_server.listen(port)
    logger.info("web is running on %s:%s", host, port)
    IOLoop.current().start()

