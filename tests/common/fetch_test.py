
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from ssguan import config
from ssguan.commons import fetch, webb, database, loggingg
from ssguan.modules import sysprop


class WebTestCase(AsyncHTTPTestCase):
    """Base class for webb tests that also supports WSGI mode.

    Override get_handlers and get_app_kwargs instead of get_app.
    Append to wsgi_safe to have it run in wsgi_test as well.
    """
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        loggingg.install_module()
        webb.install_module()
        
    def get_app(self):
        self.app = Application(self.get_handlers(), **self.get_app_kwargs())
        return self.app

    def get_handlers(self):
        raise NotImplementedError("WebTestCase.get_handlers")

    def get_app_kwargs(self):
        return {"cookie_secret": config.webbCFG.get_session_configs()["secret_key"],
                "default_handler_class": config.webbCFG.get_settings()["default_handler_class"]}
    
        
    @classmethod
    def tearDownClass(cls):        
        webb.uninstall_module()
        loggingg.uninstall_module()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())

class FetchTest(WebTestCase):
    
    def get_handlers(self):
        
        class JsonReqHandler(webb.BaseReqHandler):
            
            def get(self, *args, **kwargs):
                self.write({"welcome":"hello"})         
        
        class HtmlReqHandler(webb.BaseReqHandler):
            
            def get(self, *args, **kwargs):
                self.write("<html ><p>abce</p></html>")      
            
        return [("/json", JsonReqHandler),
                ("/html", HtmlReqHandler),
                ]
        
    def async_http_fetch(self, path, callback, headers={}, options={}):   
        
        def cb(result):
            try:
                callback(result)
            finally:                
                self.__stop_args = result
                self.io_loop.stop()            
                 
        def af(path, callback, headers, options):
            path = self.get_url(path)            
            fet = fetch.Fetcher('async_http_fetch', async=True, io_loop=self.io_loop)
            fet.http_fetch(path, cb, headers=headers, options=options)
        self.io_loop.add_timeout(10, af, path, callback, headers, options)
        self.io_loop.start()
        
    
    def test_http_fetch(self):
        def cb(result):
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.content_json, {"welcome":"hello"})
        self.async_http_fetch("/json", cb)
        
        def cb2(result):
            self.assertEqual(result.content, "<html ><p>abce</p></html>")
        self.async_http_fetch("/html", cb2)
        
