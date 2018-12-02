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

from ssguan.commons import fetch, utility
from ssguan.commons.schedule import CJRunner


class HousePrice163(CJRunner):
    
    def run(self, cjrunlog, caller):
        def cb(result):
            cj = result.content_json
            print cj
            
            
#         fetcher.http_fetch("http://xf.house.163.com/gz/trade/salesrecord/0SLX-1-1000.html", cb)
        fetcher = fetch.Fetcher(async=False)
        fetcher.http_fetch("http://localhost:8000/jinmao.txt", cb)
        

        
