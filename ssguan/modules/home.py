from ssguan import config
from ssguan.commons.error import NoFoundError
from ssguan.modules.auth import AuthReqHandler


class HomeHandler(AuthReqHandler):
    
    def prepare(self):
        raise NoFoundError("URI", self.request.uri)

def install_module():    
    config.webbCFG.add_handler("/", "ssguan.modules.HomeHandler")
    
def uninstall_module():
    config.webbCFG.delete_handler("/")
    return True