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
import compileall
import os
from re import compile
import re
import shutil
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contrib'))
import web


import conf
from core import ioutil

class BuildError(Exception):
    """Raised when by build error."""

class Build(object):
    
    BUILD_DIRNAME = '.build'
    LOG_FILENAME = "guan.log"
    ZIP_INST_NAME = "GUAN_%s_inst.zip" % (conf.G_VERSION)
    ZIP_SRC_NAME = "GUAN_%s_src.zip" % (conf.G_VERSION)
    
    def __init__(self, buildpath):
        self.__projectpath = os.path.dirname(__file__)
        if not os.path.exists(buildpath):
            os.mkdir(buildpath)
        else:
            if len (os.listdir(buildpath)) >= 0 and self.__projectpath != buildpath:
                self.__rmtree(buildpath)
                os.makedirs(buildpath)
            else:
                raise BuildError("the buildpath - %s is not empty." % buildpath)
                
        self.__temppath = buildpath + "/" + self.BUILD_DIRNAME
        self.__buildpath = buildpath
    
    def __ignore_patterns(self):
        return shutil.ignore_patterns(".git", ".gitignore")
      
    def __rmtree(self, path):
        while os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        
    def __make_dir(self, name, rootpath):
        dirname = rootpath + os.sep + name
        os.makedirs(dirname)
        
    def __copy_file(self, name, topath):
        srcpath = self.__projectpath + os.sep + name
        shutil.copy(srcpath, topath)
        
    def __copy_dir(self, name, topath, existed=False):
        srcpath = self.__projectpath + os.sep + name
        if existed:
            for root, dirs, files in os.walk(srcpath):
                for filename in files:
                    path = os.path.join(root, filename)   
                    shutil.copyfile(path, '%s/%s' % (topath, filename))
        else:
            shutil.copytree(srcpath, topath + os.sep + name)
    
    def __copy_sources(self):
        ioutil.delete_files(self.__projectpath, ".pyc")
        shutil.copytree(self.__projectpath, self.__temppath, ignore=self.__ignore_patterns())
        
        self.__rmtree("%s/.settings" % self.__temppath)
        self.__rmtree("%s/test" % self.__temppath)
        
        os.remove("%s/testentry.py" % self.__temppath)
        os.remove("%s/yuicompressor-2.4.8.jar" % self.__temppath)
        os.remove("%s/compiler.jar" % self.__temppath)
        os.remove("%s/build.py" % self.__temppath)
        os.remove("%s/.pydevproject" % self.__temppath)
        os.remove("%s/.project" % self.__temppath)
        
        self.__rmtree("%s/static" % self.__temppath)
        
        self.__rmtree("%s/work" % self.__temppath)
        self.__rmtree("%s/.git" % self.__temppath)
        self.__make_dir('work', self.__temppath)
        self.__make_dir('work/log', self.__temppath)
        self.__make_dir('work/sessions', self.__temppath)
        self.__make_dir('work/data', self.__temppath)
        
    def __compile_sources(self):
        ioutil.delete_files(self.__temppath, ".pyc")
        ioutil.delete_files(self.__temppath, ".wsgic")
        compileall.compile_dir(self.__temppath, force=True)
    
        
    def __run_tests(self):
        import testentry
        result = testentry.main()
        return result
    
    def __process_staticfiles(self):
        staticpath = "%s/static" % self.__temppath
        
        os.makedirs(staticpath)
        self.__copy_file("static/favicon.ico", staticpath)
        self.__copy_file("static/index.html", staticpath)
        self.__copy_file("static/privacy.html", staticpath)
        self.__copy_file("static/sla.html", staticpath)
        self.__make_dir("js", staticpath)
        self.__make_dir("html", staticpath)
        self.__make_dir("css", staticpath)
        self.__make_dir("images", staticpath)
        self.__make_dir("fonts", staticpath)
        
        self.__copy_dir("static/app/images", "%s/images" % staticpath, existed=True)
        self.__copy_file("static/contrib/fontawesome/fonts/fontawesome-webfont.ttf", "%s/fonts" % staticpath)
        self.__copy_file("static/contrib/fontawesome/fonts/fontawesome-webfont.woff", "%s/fonts" % staticpath)
        self.__copy_file("static/contrib/fontawesome/fonts/fontawesome-webfont.woff2", "%s/fonts" % staticpath)
        self.__copy_file("static/contrib/bootstrap/fonts/glyphicons-halflings-regular.ttf", "%s/fonts" % staticpath)
        self.__copy_file("static/contrib/bootstrap/fonts/glyphicons-halflings-regular.woff", "%s/fonts" % staticpath)
        
        for root, dirs, files in os.walk("%s/images" % staticpath):
            for filename in files:
                if not filename.endswith(".png"):
                    path = os.path.join(root, filename)
                    os.remove(path)
                    
        with  open(self.__projectpath + os.sep + "static/app/js/conf.js", "r+") as conffile:
            for line in conffile:
                if ".html" in line:
                    p = compile(r"'(.+).html'")
                    m = p.search(line)
                    self.__copy_file("static/%s.html" % m.group(1), "%s/html" % staticpath)
                    
            conffile.close()
                
        
        
    def __minify_jscss(self):
        jscssdirname = ".jscss"
        self.__make_dir(jscssdirname, self.__buildpath)
        jscssdir = "%s/%s" % (self.__buildpath, jscssdirname)
        
        def proc_confjs(confjsfile, jsallinonefile):
            for line in confjsfile:
                if ".html" in line:
                    p = compile(r"'(.+).html'")
                    m = p.search(line)
                    line = line.replace(os.path.split(m.group(1))[0], "html")
                jsallinonefile.write(line)
                
        
        cssallinonefile = open("%s/styles.css" % jscssdir, "w+")
        jsallinonefile = open("%s/scripts.js" % jscssdir, "w+")
        entryjsfile = open("%s/entry.js" % jscssdir, "w+")
        with open(self.__projectpath + "/static/entry.js", "r+") as entryfile:
            for entryline in entryfile:
                if ".js" in entryline and 'i18n.js' not in entryline:
                    p = compile(r"'(.+).js'")
                    m = p.search(entryline)
                    with open("%s/static/%s.js" % (self.__projectpath, m.group(1))) as jstmpfile:
                            if "conf" in m.group(1):
                                proc_confjs(jstmpfile, jsallinonefile)
                            else:
                                for line in jstmpfile:
                                    jsallinonefile.write(line)
                            jstmpfile.close()
                        
                elif ".css" in entryline:
                    p = compile(r"'(.+).css'")
                    m = p.search(entryline)
                    with open("%s/static/%s.css" % (self.__projectpath, m.group(1))) as csstmpfile:
                        for line in csstmpfile:
                            cssallinonefile.write(line)
                        csstmpfile.close()
                
                if "BUILD PLACEHOLDER" in entryline:
                    entryjsfile.write("addJS('js/scripts.min.js');addCSS('css/styles.min.css');");
                elif 'i18n.js' in entryline:
                    entryjsfile.write(entryline)
                else:
                    if ".js" not in entryline and ".css" not in entryline:
                        entryjsfile.write(entryline)
                        
        cssallinonefile.close()
        jsallinonefile.close()
        entryjsfile.close()
       
        cmd = "java -jar yuicompressor-2.4.8.jar -o %s %s" % (".css$:.min.css", "%s/*.css" % jscssdir)
        os.system(cmd)
        
        cmd = "java -jar compiler.jar --language_in ECMASCRIPT5 --js %s --js_output_file %s" % ("%s/scripts.js" % jscssdir, "%s/scripts.min.js" % (jscssdir))
        os.system(cmd)
        
        cmd = "java -jar compiler.jar --language_in ECMASCRIPT5 --js %s --js_output_file %s" % ("%s/entry.js" % jscssdir, "%s/entry.min.js" % (jscssdir))
        os.system(cmd)
        
        shutil.copy("%s/scripts.min.js" % (jscssdir), "%s/static/js" % self.__temppath)
        shutil.copy("%s/entry.min.js" % (jscssdir), "%s/static/entry.js" % self.__temppath)
        shutil.copy("%s/styles.min.css" % (jscssdir), "%s/static/css" % self.__temppath)
        
        self.__rmtree(jscssdir)

    
    def __create_package(self):
        ioutil.delete_files(self.__temppath, ".py")
        ioutil.zip_dir(self.__temppath, "%s/%s" % (self.__buildpath, self.ZIP_INST_NAME))
        ioutil.zip_dir(self.__projectpath, "%s/%s" % (self.__buildpath, self.ZIP_SRC_NAME))
        
    def __clean_temppath(self):
        self.__rmtree(self.__temppath)
    
    def build(self):
        if not os.path.exists(self.__projectpath):
            raise BuildError("project path %s does not exist." % self.__projectpath)
        if os.path.exists(self.__temppath):
            shutil.rmtree(self.__temppath)
        
        print '----build start-------'
        print '----running testing scripts----'
        result = self.__run_tests()
        if result is True:
            print '----copying sources-------'
            self.__copy_sources()
            print '----compile sources-------'
            self.__compile_sources()
            print '----process static files------'
            self.__process_staticfiles()
            print '----minify js and css-------'
            self.__minify_jscss()
            print '----zip installation package------'
            self.__create_package()
        else:
            print '----build is stopped since the codes are not passed the test scripts.'
        
        print '----cleaning build files-------'
        self.__clean_temppath()
        print '----build end-------'

def main():
    print "usage: build [build path]"
    if len(sys.argv) < 2:
        raise BuildError("build path is not passed as the first argument.")
    buildpath = sys.argv[1]
    build = Build(buildpath)
    build.build()

if __name__ == "__main__":
    main()
