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
from core import i18n, log, cache, sysprop, strutil
from core.handler import Handler, LoginHandler, LogoutHandler, \
    BaseDispatcher
import migration
import web


class SysManDispatcher(BaseDispatcher):
    
    def GET(self):
        render = web.template.frender("core/sysman.html")
        return render()
    
    def _get_handler(self, action):
        mh = {}
        mh['fetchmigrations'] = MigrationSmHandler()
        mh['fetchlogs'] = LogSmHandler()
        mh['fetchi18ns'] = I18nSmHandler()
        mh['fetchsysprops'] = SysPropSmHandler()
        mh['viewcache'] = CacheSmHandler()
        mh['login'] = LoginHandler()
        mh['logout'] = LogoutHandler()
        return mh[action]
    
class MigrationSmHandler(Handler):
    
    def execute(self):
        action = self._get_str_parameter("action","")
        if action == 'migrate':
            migration.migrate(self._get_user_id())
        elif action == 'downgrade':
            ver_id = self._get_int_parameter("verid")
            migration.downgrade(ver_id, self._get_user_id())
        
        migrations = migration.fetch_migrations(self._get_user_id())
        html = "<div class='sysman-buttonbar'><span onclick='sysman.migrate()' title='Migrate'>Migrate</span></td></div>"
        html += "<table>"
        for mig in migrations:
            tr = "<tr>"
            tr += "<td><p>%d</p></td>" % mig.ver_id
            tr += "<td><p>%r</p></td>" % mig.is_upgraded
            tr += "<td><p>%r</p></td>" % mig.migration_time
            tr += "<td><p>%r</p></td>" % mig.modifier_id
            tr += "<td><p>%r</p></td>" % mig.created_time
            tr += "<td><p>%r</p></td>" % mig.modified_time
            tr += "<td><span onclick='sysman.downgrade(\"%s\")' title='Downgrade'>X</span></td>" % (mig.ver_id)
            tr += "</tr>"
            html += tr
        html += "</table>"
        return html
        
    
class I18nSmHandler(Handler):
    
    def execute(self):
        i18ns = i18n.fetch_i18ns()
        html = "<table>"
        for result in i18ns:
            tr = "<tr>"
            tr += "<td><p>%s</p></td>" % result.i1_key
            tr += "<td><p>%s</p></td>" % result.i1_type
            tr += "<td><p>%s</p></td>" % result.i1_locale
            tr += "<td><p>%s</p></td>" % result.i1_message
            tr += "<td><p>%r</p></td>" % result.modifier_id
            tr += "<td><p>%r</p></td>" % result.created_time
            tr += "<td><p>%r</p></td>" % result.modified_time
            tr += "</tr>"
            html += tr
        html += "</table>"
        return html

class LogSmHandler(Handler):
    
    def execute(self):
        level = self._get_str_parameter("level", "ERROR")
        offset = self._get_int_parameter("offset", 0)
        levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
        level = "ERROR" if level not in levels else level
        pager = log.fetch_logs(level, limit=1000, offset=offset)
        html = "<select id='logLevelSelt' name='level' onchange='sysman.fetchlogs()'>"
        for l in levels:
            selected = "selected" if l == level else ''
            html += "<option value='%s' %s>%s</option>" % (l, selected , l)
        html += "</select>"
        html += "<br/><table>"
        for result in pager.records:
            tr = "<tr>"
            tr += "<td><p>%s</p></td>" % result.l_level
            tr += "<td><p>%s</p></td>" % strutil.replce_html_entities(result.l_message)
            tr += "<td><p>%r</p></td>" % result.logged_time
            tr += "</tr>"
            html += tr
        html += "</table>"
        return html

class CacheSmHandler(Handler):
    def execute(self):
        action = self._get_str_parameter("action")
        if action == 'delcache':
            caKey = self._get_str_parameter('caKey')
            cache.delete(caKey)
            
        cl = cache.populate()
        html = "<table>"
        for ca in cl:
            tr = "<tr>"
            tr += "<td><p>%s</p></td>" % ca['key']
            value = strutil.replce_html_entities(ca['value'])
            tr += "<td><p>%s</p></td>" % (value if len(value) < 50 else value[0:50] + "...")
            tr += "<td><p>%d</p></td>" % ca['hits']
            tr += "<td><span onclick='sysman.delcache(\"%s\")' title='Delete'>X</span></td>" % (ca['key'])
            tr += "</tr>"
            html += tr
            
        html += "</table>"
        return html

class SysPropSmHandler(Handler):

    def execute(self):
        sysprops = sysprop.fetch_sysprops()
        html = "<table>"
        for result in sysprops:
            tr = "<tr>"
            tr += "<td><p>%s</p></td>" % result.p_key
            tr += "<td><p>%s</p></td>" % result.p_value
            tr += "<td><p>%r</p></td>" % result.modifier_id
            tr += "<td><p>%r</p></td>" % result.created_time
            tr += "<td><p>%r</p></td>" % result.modified_time
            tr += "</tr>"
            html += tr
        html += "</table>"
        return html
