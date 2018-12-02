from ssguan.ignitor.auth.handler import AuthReqHandler
from ssguan.ignitor.base.error import NoFoundError


class HomeHandler(AuthReqHandler):
    
    def prepare(self):
        raise NoFoundError("URI", self.request.uri)