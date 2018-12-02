
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from ssguan.ignitor.orm import dbpool, config as orm_config
from ssguan.ignitor.web import  config as web_config
from ssguan.ignitor.web.handler import BaseReqHandler


class FetchTestCase(AsyncHTTPTestCase):
    """Base class for web tests that also supports WSGI mode.

    Override get_handlers and get_app_kwargs instead of get_app.
    Append to wsgi_safe to have it run in wsgi_test as well.
    """
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        
        
    def get_app(self):
        self.app = Application(self.get_handlers(), **self.get_app_kwargs())
        return self.app

    def get_handlers(self):
        raise NotImplementedError("WebTestCase.get_handlers")

    def get_app_kwargs(self):
        return {"cookie_secret": web_config.get_sessionConfig().secret_key,
                "default_handler_class": web_config.get_settings()["default_handler_class"]}
    
        
    @classmethod
    def tearDownClass(cls):        
        dbpool.drop_db(orm_config.get_default_dbinfo())

class FetchTest(FetchTestCase):
    
    def get_handlers(self):
        
        class JsonReqHandler(BaseReqHandler):
            
            def get(self, *args, **kwargs):
                self.write({"welcome":"hello"})         
        
        class HtmlReqHandler(BaseReqHandler):
            
            def get(self, *args, **kwargs):
                self.write("<html ><p>abce</p></html>")      
            
        return [("/json", JsonReqHandler),
                ("/html", HtmlReqHandler),
                ]
    