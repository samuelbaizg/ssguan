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

import os
import sys

import click

import ssguan
from ssguan import config


reload(sys)
sys.setdefaultencoding('utf-8')

class ClickContext(object):
    
    def __init__(self):
        self.verbose = False
        self.add_sys_path = True
        self.loggingg_config = os.path.join(os.path.dirname(__file__) , "config", "loggingg.properties")
        self.config = os.path.join(os.path.dirname(__file__) , "config", "config.properties")

_default_ctx = ClickContext()
pass_context = click.make_pass_decorator(ClickContext, ensure=True)

@click.group()
@click.option('--loggingg_config', default=_default_ctx.loggingg_config,
              help="logging config file for ssguan logging", show_default=True)
@click.option('--config', default=_default_ctx.config,
              help="config file for ssguan global settings", show_default=True)
@click.option('--add_sys_path/--not_add_sys_path', default=_default_ctx.add_sys_path, is_flag=True,
              help='add current working directory to python lib search path')
@click.version_option(version=ssguan.__version__, prog_name=ssguan.__name__)
@pass_context
def cli(ctx, **kwargs):
    """
    A Powerful Content Crawling Analytics Management Engine
    """
    if kwargs['add_sys_path']:
        sys.path.append(os.getcwd())
    ctx.loggingg_config = kwargs['loggingg_config']
    ctx.config = kwargs['config']
    from ssguan.commons import loggingg
    loggingg.fileConfig(ctx.loggingg_config)
    config.fileConfig(ctx.config)
    
@cli.command()
@click.option('--host', default="0.0.0.0",
              help="web listener bind to host", show_default=True)
@click.option('--port', default=8080,
              help="web listener bind to port", show_default=True)
@pass_context
def webapi(ctx, host, port):
    """
    Run Content Console Web Server
    """
    from ssguan.commons import webb
    webb.startup(host, port)

@cli.command()
@pass_context
def install(ctx):
    """
    Install ssguan
    """
    from ssguan.modules import update
    update.install()

@cli.command()
@pass_context
def upgrade(ctx):
    """
    Upgrade ssguan to the latest version
    """
    from ssguan.modules import update
    update.upgrade()

def main():
    cli(sys.argv[1:])    

if __name__ == '__main__':
    main()
